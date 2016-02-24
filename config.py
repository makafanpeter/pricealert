import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    OAUTH_CREDENTIALS =  {
    'facebook': {
          'id': '470154729788964',
          'secret': '010cc08bd4f51e34f3f3e684fbdea8a7'
      },
      'google': {
          'id': '763910754530-rqig5i0qt95f2832bdkg15m49580rhtl.apps.googleusercontent.com',
          'secret': 'KA5kZILEXedg8SuQsied7MfW'
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
