from flask import Flask, render_template
import os
import db
from datetime import timedelta


def create_app():
    print('create app(config=None)run')
    # 定义 static 默认目录和路径,加载实例配置
    app = Flask(__name__, static_folder='', static_url_path='', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='hard to guess',
        DATABASE=os.path.join(app.instance_path, 'cat.db'),
        SEND_FILE_MAX_AGE_DEFAULT=timedelta(seconds=1)
    )
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化数据库
    db.init_app(app)

    # the minimal flask application
    @app.route('/')
    def home():
        return render_template('home.html')
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.post import post_bp
    # 注册蓝本
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/a')
    # 注册时候指定的路由前缀优先级高
    # admin.admin   GET        /a/admin
    # url_for('admin')
    app.register_blueprint(post_bp)
    return app
