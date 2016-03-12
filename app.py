from flask import Flask, render_template, request, jsonify, url_for, redirect, abort
from flask.ext.sqlalchemy import SQLAlchemy
import os
import re
import lxml.html as lh
from bs4 import BeautifulSoup
import requests
import string
from rq import Queue
from rq.job import Job
from worker import conn
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from oauth import OAuthSignIn
from sqlalchemy import or_, and_

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'

task_queue = Queue(connection=conn)

from models import *


##########
# helper #
##########

def crawl(url):
    errors = []
    reg = re.compile(r'^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$')
    match = reg.search(url)
    if match:
        site = match.groups()[2];
        merchant = Merchant.query.filter_by(url=site).first()
        if merchant:
            try:
                r = requests.get(url)
            except Exception as e:
                print(e)
                errors.append(
                    "Unable to get URL. Please make sure it's valid and try again."
                )
                return {"error": errors}

            content = r.text
            nameparser = ProductNameParser.query.filter_by(merchant_id=merchant.id).first()
            priceparser = ProductPriceParser.query.filter_by(merchant_id=merchant.id).first()
            imageparser = ProductImageParser.query.filter_by(merchant_id=merchant.id).first()
            if nameparser and priceparser and imageparser:
                etree = lh.fromstring(content)
                title_elements = etree.xpath(nameparser.xpath)
                price_elements = etree.xpath(priceparser.xpath)
                image_elements = etree.xpath(imageparser.xpath)
                # print(image_elements,title_elements,price_elements)
                if len(title_elements) >= 1 and len(price_elements) >= 1 and len(image_elements) >= 1:
                    titleElement = title_elements[0]
                    priceElement = price_elements[0]
                    imageElement = image_elements[0]
                    productNameSoup = BeautifulSoup(lh.tostring(titleElement), 'lxml')
                    productPriceSoup = BeautifulSoup(lh.tostring(priceElement), 'lxml')
                    productImageSoup = BeautifulSoup(lh.tostring(imageElement), 'lxml')

                    #
                    title = productNameSoup.find(nameparser.elementTag,
                                                 {nameparser.tagAttribute: nameparser.attributeValue})
                    product_name = title.get_text().strip()

                    #
                    productPrice = productPriceSoup.find(priceparser.elementTag,
                                                         {priceparser.tagAttribute: priceparser.attributeValue})
                    price = lh.fromstring(productPrice.contents[0]).text
                    price_dec = float(re.sub("[^0-9.]*", '', price))

                    #
                    imageUrl = " "
                    productImage = productImageSoup.find(imageparser.elementTag).get(imageparser.tagAttribute)
                    image_reg = re.compile(
                        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
                    imageMatch = image_reg.search(productImage)
                    if imageMatch:
                        imageUrl = imageMatch.group(0)

                    return Product(name=product_name, url=url, price=price_dec, imageUrl=imageUrl)

    errors.append(
        "Unable to get URL. Please make sure it's valid and try again."
    )
    return {"error": errors}


def crawl_and_save(url):
    errors = []
    try:
        newproduct = crawl(url)
        if type(newproduct) == Product:
            product = Product.query.filter_by(name=newproduct.name).first()
            if not product:
                product = Product(name=newproduct.name, url=url, price=newproduct.price, imageUrl=newproduct.imageUrl)
                db.session.add(product)
                db.session.commit()
            else:
                product.price = product.price
                db.session.add(product)
            history = PriceHistory(currentPrice=product.price, product_id=product.id)
            db.session.add(history)
            db.session.commit()
            return product.id
    except Exception as e:
        print(e)
        errors.append("Unable to add item to database.")
        return {"error": errors}
    errors.append(
        "Unable to get URL. Please make sure it's valid and try again."
    )
    return {"error": errors}


############
# Flask    #
###########

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/index')
@app.route('/', methods=['GET'])
@login_required
def index():
    print(current_user.username)
    return render_template('index.html')


@app.route('/crawl', methods=['POST'])
@login_required
def get_counts():
    # get url
    if not request.json:
        abort(400)
    data = request.json.get('url')
    url = data
    url = re.sub("https://|http://", "", url)
    # form URL, id necessary
    if 'http://' not in url[:7]:
        url = 'http://' + url
    # start job
    job = task_queue.enqueue_call(
        func=crawl_and_save, args=(url,), result_ttl=5000
    )
    # return created job id
    return job.get_id()


@app.route('/deals')
def list_deals():
    products = Product.query.all()
    return render_template('deals.html', products=products)


@app.route("/results/<job_key>", methods=['GET'])
@login_required
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        if type(job.result) == dict:
            return jsonify(job.result), 500
        product = Product.query.filter_by(id=job.result).first()
        return jsonify(product.serialize)
    else:
        return "Nay!", 202


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, picture = oauth.callback()
    user = User.query.filter_by(email=email).first()
    if not user:
        try:
            user = User(username=username, picture=picture, email=email)
            db.session.add(user)
            db.session.commit()
            membership = OAuthMembership(provider=provider, provider_userid=social_id, user_id=user.id)
            db.session.add(membership)
            db.session.commit()
        except Exception as e:
            print(e)
    login_user(user, True)
    token = user.generate_auth_token(1600)
    # return redirect(url_for('index', token = token))
    return redirect(url_for('index'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/createalert/<int:id>', methods=['POST'])
@login_required
def add_alert(id):
    if not request.json:
        abort(400)
    user_id = current_user.id
    targetPrice = float(request.json.get('targetPrice'))
    tweetAt = request.json.get('tweetAt')
    product = Product.query.filter_by(id=id).first()
    if product:
        # find existing Alert
        alert = Alert.query.filter(and_(Alert.user_id == user_id, Alert.product_id == product.id)).first()
        if alert:
            alert.targetPrice = targetPrice
            alert.tweetAt = tweetAt
            alert.currentPrice = product.price
        else:
            alert = Alert(targetPrice=targetPrice, currentPrice=product.price, tweetAt=tweetAt, user_id=user_id,
                          product_id=product.id)
        try:
            db.session.add(alert)
            db.session.commit()
            return jsonify({'result': True}), 201
        except Exception as e:
            print(e)

    return jsonify({"error": "Unable to create alert."}), 400


@app.route('/myalerts', methods=['GET'])
@login_required
def my_alerts():
    user_id = current_user.id
    alerts = Alert.query.filter_by(user_id=user_id).all()
    myAlerts = []
    for value in alerts:
        product = value.product
        alert = {"id": product.id, "productImage": product.imageUrl, "productName": product.name,
                 "currentPrice": value.currentPrice, "targetPrice": value.targetPrice,
                 "reachedTarget": value.reachedTarget}
        myAlerts.append(alert)

    return jsonify(alerts=myAlerts)


if __name__ == '__main__':
    app.run(threaded=True,
            host='0.0.0.0'
            )
