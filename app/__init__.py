# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager
from app.models.base import db
from flask_admin import Admin
from app.view_models.admin import serverinfoview, businessview, scanview, roleview, instanceview
__author__ = 'caijinxu'

login_manager = LoginManager()


def register_web_blueprint(app):
    from app.web import web
    app.register_blueprint(web)


def create_app(config=None):
    app = Flask(__name__)

    #: load default configuration
    app.config.from_object('app.settings')
    app.config.from_object('app.secure')

    # 注册login模块
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.login_message = '请先登录或注册'

    register_web_blueprint(app)

    # 注册SQLAlchemy
    db.init_app(app)

    # 注册国际化
    from flask_babelex import Babel
    babel = Babel(app)

    # # 注册admin
    admin = Admin(app, template_mode='bootstrap3', base_template="base.html")
    admin.add_view(serverinfoview)
    admin.add_view(businessview)
    admin.add_view(scanview)
    admin.add_view(roleview)
    admin.add_view(instanceview)
    return app

