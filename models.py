from app import db
from sqlalchemy.orm import relationship

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
