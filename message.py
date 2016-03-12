



def send_tweet(tweetAt, product, currentPrice):
    message = "Hey @{0},{1} is on sale for {2} at {3} #PRICEALERT".format(tweetAt, product.name,currentPrice, product.url)
    print(message)

def send_email(user, product, currentPrice):
    print("I am sending an email")
