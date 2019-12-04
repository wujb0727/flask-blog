import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


# 通用配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kalfa53465gEFDSFfdg5#$&$2hdfd%&#$%#&asf5413(44|)'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    # 指定保存文件的本地路径
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    AVATAR_FOLDER = 'avatars'
    # os.getcwd() + r'\uploads\avatars'
    # 指定上传的文件类型
    ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
    # 指定上传的文件大小（以字节为单位）
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 邮箱配置
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '15807277340@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'qqzxc095'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'  # 邮件主题前缀
    FLASKY_MAIL_SENDER = 'Flasky Admin <15807277340@163.com>'

    # 分页时每页多少条数据
    FLASKY_POSTS_PER_PAGE = 10


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
