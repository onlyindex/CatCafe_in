from flask import Flask, render_template, request
import os
import db
from db import get_db
from datetime import timedelta


def create_app():
    print('create app(config=None)run')
    # 定义 static 默认目录和路径,加载实例配置
    app = Flask(__name__, static_folder='', static_url_path='', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='hard to guess',
        # DATABASE=os.path.join(app.instance_path, 'cat.db'),
        SEND_FILE_MAX_AGE_DEFAULT=timedelta(seconds=1),
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
    db.init_app(app)

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
    # @app.route('/')
    # def home():
    #     return redirect(url_for('home'))
    # 展示首页
    # _(:зゝ∠)_最新日志取最近七条记录
    # _(:зゝ∠)_评论最多的、最喜欢的、分享最多的7条日志记录
    @app.route('/', methods=['GET'])
    def home():
        if request.method == 'GET':
            error = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'select p.post_id, p.post_title, date(p.post_timestamp) as post_timestamp,p.author_alias,p.author_id '
                'from post as p  '
                'order by p.post_timestamp desc ')
            posts = cursor.fetchall()
        return render_template('home.html', posts=posts)
    return app
