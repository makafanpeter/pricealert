from app import db
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask.ext.login import UserMixin
from datetime import datetime
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


class Merchant(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    url = db.Column(db.String())

    """docstring forMerchant"""
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return '<id {}>'.format(self.id)


class ProductNameParser(db.Model):
     __tablename__ = 'productnameparsers'
     id = db.Column(db.Integer, primary_key=True)
     xpath = db.Column(db.String())
     elementTag = db.Column(db.String())
     tagAttribute = db.Column(db.String())
     attributeValue = db.Column(db.String())
     merchant_id = db.Column(db.Integer,db.ForeignKey('merchants.id'))
     merchant = relationship(Merchant)

     def __init__(self, xpath, elementTag,tagAttribute, attributeValue,merchant_id):
            self.xpath = xpath
            self.elementTag = elementTag
            self.tagAttribute = tagAttribute
            self.attributeValue = attributeValue
            self.merchant_id  =  merchant_id

     def __repr__(self):
        return '<id {}>'.format(self.id)


class ProductPriceParser(db.Model):
     __tablename__ = 'productpriceparsers'
     id = db.Column(db.Integer, primary_key=True)
     xpath = db.Column(db.String())
     elementTag = db.Column(db.String())
     tagAttribute = db.Column(db.String())
     attributeValue = db.Column(db.String())
     merchant_id = db.Column(db.Integer,db.ForeignKey('merchants.id'))
     merchant = relationship(Merchant)
     def __init__(self, xpath, elementTag,tagAttribute, attributeValue,merchant_id):
        self.xpath = xpath
        self.elementTag = elementTag
        self.tagAttribute = tagAttribute
        self.attributeValue = attributeValue
        self.merchant_id  =  merchant_id

     def __repr__(self):
         return '<id {}>'.format(self.id)


class ProductImageParser(db.Model):
     __tablename__ = 'productimageparsers'
     id = db.Column(db.Integer, primary_key=True)
     xpath = db.Column(db.String())
     elementTag = db.Column(db.String())
     tagAttribute = db.Column(db.String())
     attributeValue = db.Column(db.String())
     merchant_id = db.Column(db.Integer,db.ForeignKey('merchants.id'))
     merchant = relationship(Merchant)

     def __init__(self, xpath, elementTag,tagAttribute, attributeValue,merchant_id):
        self.xpath = xpath
        self.elementTag = elementTag
        self.tagAttribute = tagAttribute
        self.attributeValue = attributeValue
        self.merchant_id  =  merchant_id

     def __repr__(self):
            return '<id {}>'.format(self.id)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    url = db.Column(db.String())
    price = db.Column(db.Float)
    imageUrl = db.Column(db.String())

    def __init__(self, name, url,price, imageUrl):
        self.name = name
        self.url = url
        self.price = price
        self.imageUrl = imageUrl

    def __repr__(self):
        return '<id {}>'.format(self.id)

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         return {
            "id" : self.id,
            "name": self.name,
            "url" : self.url,
            "price": self.price,
            "imageUrl": self.imageUrl
            }



class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    picture = db.Column(db.String)
    email = db.Column(db.String)
    password_hash = db.Column(db.String(64))

    def __init__(self, username, picture, email  ):
        self.username = username
        self.picture = picture
        self.email = email

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    #Add a method to generate auth tokens here

    def generate_auth_token(self, expiration=600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'id': self.id })

    #Add a method to verify auth tokens here
    @staticmethod
    def verify_auth_token(token):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['id']
    	return user_id

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         return {
            "id" : self.id,
            "username": self.username,
            "picture" : self.picture
            }



class OAuthMembership(db.Model):
    """docstring for """
    __tablename__ = 'oauthmemberships'
    provider = db.Column(db.String(30), primary_key=True)
    provider_userid =  db.Column(db.String(100), primary_key=True)
    user_id =  db.Column(db.Integer,db.ForeignKey('users.id'))
    user = relationship(User)

    def __init__(self, provider , provider_userid , user_id):
        self.provider = provider
        self.provider_userid = provider_userid
        self.user_id =  user_id

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         return {
         "provider" : self.provider,
         "provideruserid": self.provider_userid
         }


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    targetPrice = db.Column(db.Float)
    currentPrice = db.Column(db.Float)
    tweetAt = db.Column(db.String)
    reachedTarget = db.Column(db.Boolean, default= False)
    user_id =  db.Column(db.Integer,db.ForeignKey('users.id'))
    product_id =  db.Column(db.Integer,db.ForeignKey('products.id'))
    createdOn = db.Column(db.DateTime, default = datetime.now())
    user = relationship(User)
    product = relationship(Product)

    def __init__(self, targetPrice, currentPrice,tweetAt, user_id, product_id ):
        self.targetPrice = targetPrice
        self.currentPrice = currentPrice
        self.tweetAt = tweetAt
        self.product_id = product_id
        self.user_id =  user_id

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         return {
         "targetPrice" : self.targetPrice,
         "currentPrice": self.currentPrice,
         "createdOn": self.createdOn
         }



class AlertHistory(db.Model):
    __tablename__ = "alerthistory"
    """docstring for AlertHistory"""
    id = db.Column(db.Integer, primary_key=True)
    currentPrice = db.Column(db.Float)
    createdOn = db.Column(db.DateTime, default = datetime.now())
    alert_id =  db.Column(db.Integer,db.ForeignKey('alerts.id'))
    alert = relationship(Alert)

    def __init__(self, currentPrice, wishlist_id):
        self.currentPrice = currentPrice
        self.wishlist_id = wishlist_id

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         return {
         "currentPrice": self.currentPrice,
         "createdOn": self.createdOn,
         "alert_id": self.alert_id
         }
