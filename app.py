from flask import Flask,render_template, request, jsonify
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





app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

task_queue = Queue(connection=conn)


from models import *

##########
# helper #
##########
def crawl_and_save(url):
    errors = []
    reg  =  re.compile(r'^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$')
    match = reg.search(url)
    if match:
        site = match.groups()[2];
        merchant = Merchant.query.filter_by(url=site).first()
        if merchant:
            try:
                r = requests.get(url)
            except Exception as e:
                print (e)
                errors.append(
                    "Unable to get URL. Please make sure it's valid and try again."
                )
                return {"error": errors}

            content = r.text
            nameparser = ProductNameParser.query.filter_by(merchant_id = merchant.id).first()
            priceparser = ProductPriceParser.query.filter_by(merchant_id = merchant.id).first()
            imageparser = ProductImageParser.query.filter_by(merchant_id = merchant.id).first()
            if nameparser and priceparser and imageparser:
                etree = lh.fromstring(content)
                title_elements = etree.xpath(nameparser.xpath)
                price_elements =  etree.xpath(priceparser.xpath)
                image_elements =  etree.xpath(imageparser.xpath)
                #print(image_elements,title_elements,price_elements)
                if len(title_elements) >= 1 and len(price_elements) >= 1 and len(image_elements) >= 1:
                    titleElement = title_elements[0]
                    priceElement = price_elements[0]
                    imageElement = image_elements[0]
                    productNameSoup= BeautifulSoup(lh.tostring(titleElement),'lxml')
                    productPriceSoup= BeautifulSoup(lh.tostring(priceElement),'lxml')
                    productImageSoup = BeautifulSoup(lh.tostring(imageElement),'lxml')

                    #
                    title = productNameSoup.find(nameparser.elementTag,{nameparser.tagAttribute:nameparser.attributeValue})
                    product_name = title.get_text().strip()

                    #
                    productPrice = productPriceSoup.find(priceparser.elementTag,{priceparser.tagAttribute:priceparser.attributeValue})
                    price = lh.fromstring(productPrice.contents[0]).text
                    price_dec = float(re.sub("[^0-9.]*",'',price))

                    #
                    imageUrl = " "
                    productImage = productImageSoup.find(imageparser.elementTag).get(imageparser.tagAttribute)
                    image_reg = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
                    imageMatch = image_reg.search(productImage)
                    if imageMatch:
                        imageUrl = imageMatch.group(0)

                    try:
                        product = Product.query.filter_by(name = product_name).first()
                        if not product:
                            product = Product( name= product_name, url = url,price = price_dec, imageUrl = imageUrl)
                            print(product)
                            db.session.add(product)
                            db.session.commit()
                        return product.id
                    except Exception as e:
                          print (e)
                          errors.append("Unable to add item to database.")
                          return {"error": errors}

    errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
    return {"error": errors}


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/crawl', methods=['POST'])
def get_counts():
    # get url
    if not request.json :
        abort(400)
    data = request.json.get('url')
    url = data
    print (url)
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
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        if type (job.result) == dict:
            return jsonify(job.result),500
        product = Product.query.filter_by(id=job.result).first()
        return jsonify(product.serialize)
    else:
        return "Nay!", 202


if __name__ == '__main__':
    app.run(threaded=True,
    host='0.0.0.0'
)
