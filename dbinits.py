from app import db
from models import *

sites = {
'www.konga.com':{ 'name': 'konga', "parser": {"productName":{"xpath":'//*[@id="main-content-container"]/div[2]/div/div[2]/div[2]/div[1]',"elementTag":"div","tagAttribute":"class", "attributeValue":"product-name"},"productPrice":{"xpath":'//*[@id="main-content-container"]/div[2]/div/div[2]/div[2]/div[7]/span[1]',"elementTag":"span","tagAttribute":"class", "attributeValue":"price"}} },
'www.jumia.com.ng':{ 'name': 'Jumia', "parser": {"productName":{"xpath":'/html/body/main/section[1]/div[2]/div[1]/span',"elementTag":"h1","tagAttribute":"class", "attributeValue":"title"},"productPrice":{"xpath":'/html/body/main/section[1]/div[2]/div[1]/div[4]/div[1]/span',"elementTag":"span","tagAttribute":"dir", "attributeValue":"ltr"}} } ,
'traclist.com':{ 'name': 'traclist', "parser": {"productName":{"xpath":'//*[@id="product"]/section[1]/div[2]/div[2]',"elementTag":"div","tagAttribute":"class", "attributeValue":"product-title"},"productPrice":{"xpath":'//*[@id="product"]/section[1]/div[2]/div[2]',"elementTag":"div","tagAttribute":"class", "attributeValue":"product-pricing"}} }
}

jumia = Merchant(name = "Jumia", url="www.jumia.com.ng" )

db.session.add(jumia)
db.session.commit()

productName = ProductNameParser(xpath='/html/body/main/section[1]/div[2]/div[1]/span', elementTag="h1",tagAttribute="class", attributeValue ="title",merchant_id = jumia.id)
db.session.add(productName)
db.session.commit()


productPrice = ProductPriceParser(xpath='/html/body/main/section[1]/div[2]/div[1]/div[4]/div[1]/span', elementTag="span",tagAttribute="dir", attributeValue ="ltr",merchant_id = jumia.id)
db.session.add(productPrice)
db.session.commit()


productImage = ProductImageParser(xpath='/html/body/main/section[1]/div[1]/div[3]', elementTag="img",tagAttribute="data-src", attributeValue ="ltr",merchant_id = jumia.id)
db.session.add(productImage)
db.session.commit()


konga = Merchant(name = "konga", url="www.konga.com" )

db.session.add(konga)
db.session.commit()

productName = ProductNameParser(xpath='//*[@id="main-content-container"]/div[2]/div/div[2]/div[2]/div[1]', elementTag="div",tagAttribute="class", attributeValue ="product-name",merchant_id = konga.id)
db.session.add(productName)
db.session.commit()


productPrice = ProductPriceParser(xpath='//*[@id="main-content-container"]/div[2]/div/div[2]/div[2]/div[7]/span[1]', elementTag="span",tagAttribute="class", attributeValue ="price",merchant_id = konga.id)
db.session.add(productPrice)
db.session.commit()


productImage = ProductImageParser(xpath='//*[@id="carousel-example-generic"]/div/div[1]/div', elementTag="img",tagAttribute="src", attributeValue ="price",merchant_id = konga.id)
db.session.add(productImage)
db.session.commit()




traclist = Merchant(name = "traclist", url="traclist.com" )

db.session.add(traclist)
db.session.commit()

productName = ProductNameParser(xpath='//*[@id="product"]/section[1]/div[2]/div[2]', elementTag="div",tagAttribute="class", attributeValue ="product-title",merchant_id = traclist.id)
db.session.add(productName)
db.session.commit()


productPrice = ProductPriceParser(xpath='//*[@id="product"]/section[1]/div[2]/div[2]', elementTag="div",tagAttribute="class", attributeValue ="product-pricing",merchant_id = traclist.id)
db.session.add(productPrice)
db.session.commit()


productImage = ProductImageParser(xpath='//*[@id="product"]/section[1]/div[2]/div[1]/div[1]/div/div', elementTag="div",tagAttribute="ng-click", attributeValue ="product-pricing",merchant_id = traclist.id)
db.session.add(productImage)
db.session.commit()
