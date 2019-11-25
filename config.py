import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


# 通用配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kalfa53465gEFDSFfdg5#$&$2hdfd%&#$%#&asf5413(44|)'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '15807277340@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'qqzxc095'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'  # 邮件主题前缀
    FLASKY_MAIL_SENDER = 'Flasky Admin <15807277340@163.com>'


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE") or 'sqlite:///' + os.path.join(basedir,
                                                                                            'data.sqlite3') + '?check_same_thread=False'


# 测试环境配置
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE") or 'sqlite:///' + os.path.join(basedir,
                                                                                             'data.sqlite3') + '?check_same_thread=False'


# 生产环境配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("PRO_DATABASE") or 'sqlite:///' + os.path.join(basedir,
                                                                                            'data.sqlite3') + '?check_same_thread=False'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
