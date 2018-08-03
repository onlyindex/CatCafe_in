# __init__.py 加载配置 创建实例 定义沉睡路由
import os

from flask import Flask
# from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLALCHEMY
from config import config
from yourapplication.model import db
from yourapplication.views.admin import admin
from yourapplication.views.frontend import frontend


#应用程序工厂
def create_app(test_config=None):
    # 创建 app
    app = Flask(__name__, instance_relative_config=True)
    # 配置 app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite')

    )
    # 重新加载 app 配置
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(
            test_config
        )
    # 确保实例文件存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

#创建实例
# bootstrap=Bootstrap()
mail=Mail()
moment=Moment()
db=SQLALCHEMY()




#扩展初始化

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

   # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    app.register_blueprint(admin)
    app.register_blueprint(frontend)

    #附加路由和自定义错误页面


    return app



