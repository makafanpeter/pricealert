from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.redis import RedisJobStore
from message import *
from app import db, crawl
from models import *

jobstores = {
    'default': RedisJobStore(host='127.0.0.1', port=6379)
}

scheduler = BlockingScheduler(jobstores=jobstores)


def scheduled_job():
    #
    print('This job is run every two hours.')
    alerts = Alert.query.filter_by(reachedTarget=False).all()
    print("Number of alert(s) to process =>", len(alerts))
    for alert in alerts:
        product = alert.product
        p = crawl(product.url)
        print(p)
        target_price = alert.targetPrice
        if type(p) == Product:
            current_price = p.price
            previous_price = product.price
            if current_price < target_price:
                alert.reachedTarget = True
                if alert.tweetAt:
                    send_tweet(tweetAt=alert.tweetAt, product=product, currentPrice=current_price)
                else:
                    send_email(user=alert.user, product=product, currentPrice=current_price)
            if previous_price != current_price:
                history = PriceHistory(currentPrice=current_price, product_id=product.id)
                product.price = current_price
                db.session.add(product)
                db.session.add(history)
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
            alert_history = AlertHistory(currentPrice=current_price, wishlist_id=alert.id)
            alert.currentPrice = current_price
            db.session.add(alert_history)
            db.session.add(alert)
            try:
                db.session.commit()
            except Exception as e:
                print(e)


job = scheduler.add_job(scheduled_job, 'interval', hour=2, id='price_alerts_cron', replace_existing=True)

scheduler.start()
