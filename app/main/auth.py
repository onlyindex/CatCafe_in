# 创建认证蓝图auth.py
import datetime
import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
from flask_login import login_required, login_user

from app import db
from .forms import LoginForm, SignupForm
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


# ?
def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


# 查询session.get('user_id')   g.user=get_db().excute(...,'user_id').fetchone
@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
        the database into ``g.user``."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()







# 注册视图-渲染注册表单+接受表单中的数据
@bp.route('/signup', methods=('GET', 'POST'))
def sign_up():
    """Register a new user.
        Validates that the username is not already taken. Hashes the
        password for security.
        """

    if request.method == 'POST':
        # request.form 是一个特殊类型的 dict,映射表单键值
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/signup.html')


@bp.route('/signup', methods = ['GET', 'POST'])
def sign_up():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('.login'))
    return render_template('auth/signup.html', form=form)


# 登录视图-渲染登录表单+接受表单中的数据
@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
            flash('Invalid username or password.')
        return render_template('auth/login.html', form=form)


# 用户访问未授权的 URL 时会显示登录表单，Flask-Login 会把原地址保存在查询字符串的 next 参数中，这个参数可从 request.args 字典中读取。
# 如果查询字符串中没有 next 参数，则重定向到首页。
# 记住我”也在表单中填写。如果值为 False，那么关闭浏览器后用户会话就过期 了，所以下次用户访问时要重新登录。
# 如果值为 True，那么会在用户浏览器中写入一个长 期有效的 cookie，使用这个 cookie 可以复现用户会话

@bp.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)


@bp.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


# @login_required 只让认证用户访问


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            else:
            session['known'] = True
            session['name'] = form.name.data
            form.name.data = ''
            return redirect(url_for('index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))


@bp.route('/')
def index():
    form = SignupForm()
    if form.validate_on_submit():
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           konwn=session.get('konwn', False),
                           current_time=datetime.utconw())


# 注销
@bp.route('/logout')
@login_required
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    logout_user()
    # 删除并重设用户 会话。
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
