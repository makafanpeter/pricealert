import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    OAUTH_CREDENTIALS =  {
    'facebook': {
          'id': '939475312801278',
          'secret': '33a13a651e8a0ccbbfd795b2a719bc92'
      },
      'google': {
          'id': '434855738061-2tdjkrh80gnm717rr5658u6lp8pmo4db.apps.googleusercontent.com',
          'secret': '6EjBpvzF59V9kp_Pi7BdW9QC'
      },
      'twitter': {
          'id': '3RzWQclolxWZIMq5LJqzRZPTl',
          'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
      },
}

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
