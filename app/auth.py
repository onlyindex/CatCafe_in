import functools

from flask import Blueprint, g
from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

'''session模拟
简单的用户认证 
用户会话管理 
用户登录登出'''


# 判断用户是否登陆
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        print("login_required exc")
        if g.user is None:
            return redirect(url_for('auth.signin'))


# 判断是否是管理员登录
def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        print("admin_login_required exc")
        if g.user is not None:
            if g.user[0] == 1:
                return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('auth.signin'))


@auth_bp.before_app_request
def load_logged_in_user():
    print("load_logged_in_user exc")
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("select * from user where user_id = '%s' " % user_id)
        g.user = cursor.fetchone()


# 用户注册
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 获取用户名密码
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # 连接数据库
        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = '用户名不为空.'
        elif not password:
            error = '密码不为空.'
        elif not email:
            error = '邮箱不为空'
            # 确认用户名是否已在数据库存在
        elif len(cursor.execute("select user_id from user where username = '%s' " % username).fetchall())>=1:
            error = 'user{0} is already signup.'.format(username)
            # 确认邮箱是否已在数据库存在
        elif len(cursor.execute("select user_id from user where email = '%s' " % email).fetchall())>=1:
            error = 'email{0} is already signup'.format(email)
        if error is None:
            cursor.execute("insert into user(username,email,password) values('%s','%s','%s') " % (
                username, email, generate_password_hash(password)))
            db.commit()
            flash('注册成功', 'success')
            return redirect(url_for('auth.signin'))
        flash(error, 'warning')
    return render_template('auth/signup.html')


# 用户登录
@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        cursor = db.cursor()
        cursor.execute("select * from user where username = '%s' " % username)
        user = cursor.fetchone()
        if user is None:
            error = '错误用户名'
        elif not check_password_hash(user[3], password):
            error = '错误密码'
        if error is None:
            session.clear()
            # 登录后写入session
            session['user_id'] = user[0]
            print(session)
            return redirect(url_for('home'))
        flash(error, 'warning')
    return render_template('auth/signin.html')


# 用户登出
@auth_bp.route('/signout')
def signout():
    session.clear()
    flash('成功退出', 'success')
    return redirect(url_for('auth.signin'))
