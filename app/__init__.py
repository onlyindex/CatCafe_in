# __init__.py 加载配置 创建实例 定义沉睡路由
import os

from flask import Flask

# from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLALCHEMY
from flask.ext.login import LoginManager
from config import config
# from app.model import db
from app import db
from app.views.admin import admin
from app.views.frontend import frontend
from .article import article
from app.main import main as main_blueprint
from .auth import auth as auth_blueprint


# 应用程序工厂
def create_app(test_config=None):
    # 创建 app
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    # 配置 app
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, 'app.sqlite')

    )
    # app.config['SECRET_KEY']='hard to guess string'
    # SECRET_KEY配置变量是通用秘钥,可以在 flask和第三方扩展中使用.加密强度取决于变量值的机密程度.不同程序使用不同秘钥保证其他人不知道你所用字符串
    # 为增强安全性米娅不要写入代码,而要保存在环境变量中
    # app.config dict 用来存储框架/扩展/程序本身的配置变量
    # 重新加载 app 配置
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(
            test_config
        )
    # 确保实例文件存在  ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


# 创建实例
# bootstrap=Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
# login_manager.login_view = 'auth.login'
login_manager.login_view = 'login'
# 会话保护 None、'basic' 或 'strong'，不同的安全等级
# 'strong' 时，Flask-Login 会记录客户端 IP 地址和浏览器的用户代理信息，
# login_view 属性设置登录页面 的端点。
mail = Mail()
moment = Moment()
db = SQLALCHEMY()


# 扩展初始化

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # register the database commands
    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝图  url_prefix='蓝图位置'  apply the blueprints to the app

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    # /login 路由会注册成 /auth/ login， URL  http://localhost:5000/auth/login
    # 登录页面使用的模板保存在 auth/login.html 文件中
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(article.bp, url_prefix='/article')

    app.register_blueprint(admin)
    app.register_blueprint(frontend)

    # 附加路由和自定义错误页面
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule('/', endpoint='index')

    return app
