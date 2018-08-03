import os

basedir = os.path.abspath(os.path.dirname(__file__))


# 秘钥&数据库&邮件配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASK_MAIL_SUBJECT_PREFIX = '[Catcafe]'
    FLASK_MAIL_SENDER = 'Catcafe Admin<onlyindex@gmail.com>'
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig:
    DEBUG = True
    MAIL_SERVER = 'smtp.googleemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URL = os.environ.get('DEV_DATABASE_URL')
    # or \"sqlite:///" + os.path.join(basedir, 'data-dev.sqlite')


config = {'development': DevelopmentConfig,

          'default': DevelopmentConfig
          }
