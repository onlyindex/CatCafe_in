import datetime
import functools
from flask import flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import db_session
from db import get_db
from flask_login import login_user

from app import db
from app.forms import LoginForm, SignupForm
from app.models import User


# index・_・?
# 不懂这段代码 g 是经常见但是不知道能干啥
def login_required(view):
    """View decorator that redirects anonymous users to the login page.只让认证用户访问"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        # index・_・?
        # 书上在templates/auth/login.html 我现在目录直接是templates/login.html 那我直接 url_for('login') 就可以了?

        return view(**kwargs)

    return wrapped_view

# index・_・?
# 觉得下面这个 secret(只有登录用户才可以)跟上面的login_required(匿名用户跳转到登录页面才可以访问)组合 ?
# secret 我都不知道这个路由干啥要是只是一句话提示也太浪费了吧
@app.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


# sign up
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():

    form = SignupForm(request.form)

    if request.method == 'POST' and form.validate():
        # index・_・?
        # form.validate()  vs form.validate_on_submit() 啥区别????
        # 这里确认密码 confirm_pwd 没用上? 之前在表单填写过程中在 forms. py 里面 已经对比了confirm_pwd和 password?
        # 获取用户数据(用户名,邮箱,密码)
        user = User(form.username.data, form.email.data, form.password.data)
        # 用户数据提交到数据库拉
        db_session.add(user)
        # 提交成功给消息感谢注册并跳到登录页面
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/signup')
def sign_up():
    form = SignupForm()
    # index・_・?
    # form.validate()  vs form.validate_on_submit() 啥区别????
    if form.validate_on_submit():
        return redirect(url_for('.index'))
    # .index 是啥鬼?
    return render_template('index.html',
                           form=form,
                           # session 和 db_session 是不一样的吧 知道第二个会话指的是数据库事务会话 第一个指的啥就不知道了
                           # session是不是和 cookie 是好朋友
                           # 看看我的 app.py 这个文件里面 index 吧 相应对象设置 cookie????
                           # current_time经常见,不能专门做个处理么 觉得好像没鸟用
                           name=session.get('name'),
                           konwn=session.get('konwn', False),
                           current_time=datetime.utconw())


# 注册视图-渲染注册表单+接受表单中的数据
@app.route('/signup', methods=('GET', 'POST'))
def sign_up():
    """
    Register a new user.
    Validates that the username is not already taken.
    Hashes the password for security.
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
            return redirect(url_for('login'))

        flash(error)

    return render_template('signup.html')


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('.login'))
    return render_template('signup.html', form=form)


# 登录视图-渲染登录表单+接受表单中的数据
@app.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute(
            'SEECT * FROM user WHERE username = ?', (username,)
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

    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # pass remember=True
            # 第一个参数传入用户对象,第二个参数 传入 以后是否自动登陆flask_login.login_user(user,True)
            return redirect(request.args.get('next') or url_for('main.index'))
            flash('Invalid username or password.')
        return render_template('login.html', form=form)


# 用户访问未授权的 URL 时会显示登录表单，Flask-Login 会把原地址保存在查询字符串的 next 参数中，这个参数可从 request.args 字典中读取。
# 如果查询字符串中没有 next 参数，则重定向到首页。
# 记住我”也在表单中填写。如果值为 False，那么关闭浏览器后用户会话就过期 了，所以下次用户访问时要重新登录。
# 如果值为 True，那么会在用户浏览器中写入一个长 期有效的 cookie，使用这个 cookie 可以复现用户会话

@app.route('/login', methods=['POST', 'GET'])
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    # 如果提交表单验证
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        # 获得邮箱信息
        user = User.query.filter_by(email=form.email.data).first()
        # 当用户不为空确认用户密码
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flask.flash('Logged in successfully.')
            next = request.args.get('next')
            # request.args是获取参数的,就是登陆后要跳转的页面 如果没下一页的跳转参数,那就返回首页
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return abort(400)

            return redirect(next or url_for('index'))
            # 为空提示用户名或者密不存在
        flash('Invalid username or password.')
        return render_template('auth/login.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # 获取用户名信息
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


# 注销
@app.route('/logout')
@login_required
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    logout_user()
    # 删除并重设用户 会话。
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
