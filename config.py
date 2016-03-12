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
          'id': '402931892293-hjcvg51uh811gqn5acbp88465rootr88.apps.googleusercontent.com',
          'secret': 'KpRBJvLLF-jwObxvy0zDPWDc'
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
