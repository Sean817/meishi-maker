'''
@Software: PyCharm
@File: __init__.py.py
@Author: PySean
@Time: Dec 06, 2020
'''
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_mongoengine import MongoEngine
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
# db = SQLAlchemy()
db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
photos = UploadSet('photos', IMAGES)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    configure_uploads(app, photos)
    patch_request_class(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app