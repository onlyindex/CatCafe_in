from flask import Flask, render_template, request
import os
import db
from db import get_db
# from flask_sqlalchemy import SQLAlchemy
# from flask_ckeditor import CKEditor

from datetime import timedelta


# Sword Art Online
def create_app():
    print('create app(config=None)run')
    # 定义 static 默认目录和路径,加载实例配置
    app = Flask(__name__, static_folder='', static_url_path='', instance_relative_config=True)
    app.config.from_mapping(
        # 配置文件太少了_(:з」∠)_so未分门别类放置
        SECRET_KEY='hard to guess',
        DATABASE=os.path.join(app.instance_path, 'cat.db'),
        # 设置图片文件储存位置
        PHOTO_UPLOAD_PATHUP=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads'),
        ALLOWD_EXTENSIONS=['png', 'jpg', 'jpeg', 'gif'],
        # 主题配置文件
        THEMES={'Pink': 'pink_phone', 'Blue': 'blue_phone'},
        SEND_FILE_MAX_AGE_DEFAULT=timedelta(seconds=1),
        # 最大请求报文长度
        MAX_CONTENT_LENGHT=3 * 1024 * 1024,
        # 设置会话过期时间
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
    )
    print(app.config.get('DATABASE'))
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化数据库
    # db = SQLAlchemy()
    # 实例化CKEditor类
    # ckeditor=CKEditor()
    # 使用工厂函数初始化
    db.init_app(app)
    # ckeditor.init(app)

    from app.auth import auth_bp
    from app.post import post_bp
    from app.user import user_bp
    from app.message import msg_bp
    from app.admin import admin_bp
    # 注册蓝本
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # app.register_blueprint(admin_bp, url_prefix='/a')
    # 注册时候指定的路由前缀优先级高
    # admin.admin   GET        /a/admin
    # url_for('admin')
    app.register_blueprint(post_bp)
    app.register_blueprint(user_bp)

    # the minimal flask application
    @app.route('/', methods=['GET'])
    def home():
        return render_template('base3.html')

    @app.route('/dalao', methods=['GET'])
    def dalao():
        return render_template('dalao.html')

    @app.route('/me', methods=['GET'])
    def me():
        return render_template('me2.html')

    return app
