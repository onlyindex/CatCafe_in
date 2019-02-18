import functools

from flask import Blueprint, g
from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash ,check_password_hash
from db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.signin'))
        return view(**kwargs)
    return wrapped_view


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('select * from user where id =?', (user_id,)).fetchone()


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 获取用户名密码
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # 连接数据库
        db = get_db()
        error = None

        if not username:
            error = '用户名不为空.'
        elif not password:
            error = '密码不为空.'
        elif not email:
            error = '邮箱不为空'
        elif db.execute('select id from user where username = ?', (username,)).fetchone() is not None:
            error = 'user{0} is already signup.'.format(username)
        elif db.execute('select id from user where email = ?', (email,)).fetchone() is not None:
            error = 'email{0} is already signup'.format(email)
        if error is None:
            db.execute('insert into user(username,email,password) values(?, ?, ?)',
                       (username, email, generate_password_hash(password)))
            db.commit()
            flash('注册成功')
            return redirect(url_for('auth.signin'))
        flash(error)
    return render_template('auth/signup.html')


@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('select * from user where username=?', (username,)).fetchone()
        if user is None:
            error = '错误用户名'
        elif not check_password_hash(user['password'], password):
            error = '错误密码'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        flash(error)
    return render_template('auth/signin.html')


@auth_bp.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('home'))























