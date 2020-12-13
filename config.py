'''
@Software: PyCharm
@File: config.py.py
@Author: PySean
@Time: Dec 06, 2020
'''

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.sina.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '25'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in \
                   ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = '美食Maker <pysean@sina.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGODB_SETTINGS = {
        'db': 'foods',
        'host': 'localhost',
        'port': 27017
    }
    PERMISSION = {
        'FOLLOW': 0x01,
        'COMMENT': 0x02,
        'WRITE_ARTICLES': 0x04,
        'MODERATE_COMMENTS': 0x08,
        'ADMINISTER': 0x80
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # for local dev, need access remote mongodb
    MONGODB_HOST = "127.0.0.1"
    FILE_URL_HOST = "127.0.0.1"


class TestingConfig(Config):
    DEBUG = True
    # for local dev, need access remote mongodb
    MONGODB_HOST = "127.0.0.1"
    FILE_URL_HOST = "127.0.0.1"


class ProductionConfig(Config):
    DEBUG = True
    # for local dev, need access remote mongodb
    MONGODB_HOST = "127.0.0.1"
    FILE_URL_HOST = "127.0.0.1"


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
