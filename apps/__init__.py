from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
pagedown = PageDown()


def create_app(config_name):
    """
    :param config_name: str,配置类
    :return:
    """
    app = Flask(__name__)
    # 加载Config类中的配置
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 注册主蓝图
    from apps.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from apps.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 注册api蓝图
    from apps.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
