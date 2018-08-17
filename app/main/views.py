# 程序路由
# 导入蓝本 main
# # 蓝本中的路由和视图函数
# 有点看明白 main/view.py =main/auth.py + main/article.py +.....蓝图被拆分了
# 蓝本中的路由和视图函数
from datetime import datetime
from os import abort

from flask import render_template, session, redirect, url_for, request, flash, current_app
from sqlalchemy.sql.functions import current_user

from app.main import main
from app.main.forms import EditProfileForm, EditProfileAdminForm, PostForm
from app import db
from app.models import User, Role, Post

from decorators import admin_required, permission_required
from .models import Permission


# flask 为蓝本中的端点添加命名空间
# 视图函数 index() 注册的端点是 main.index 使用 url_for('main.index')获取 url


@auth.route('/login')
def login():
    return render_template('auth/login.html')


# 蓝本中的路由和视图函数
from flask import render_template
from app.main import auth


@auth.route('/login')
def login():
    return render_template('auth/login.html')


# 傻逼了这个模板文件来自 auth/templates/auth/login.html

# 傻逼了是在  auth/view s.py 里面 写登录路由还是在auth/ auth.py 里面写登录路由


# before_app_request 处理程序在每次请求前运行
# before_request 钩子
# before_app_request 修饰器 在蓝本中使用针对程序全局请求的钩子
# 过滤未确认的账户
@auth.before_app_request
def before_request():
    if current_user.is_authenticated()
        and not current_user.confirmed
        and request.endpoint[:5] != 'auth.':
        # 请求的端点(request.endpoint 获取)不在认证蓝本中。
        # 访问认证路由要获取权限，路由的作用是让用户确认账户或执行其他账户管理操作。
        and request.endpoint != 'static':
    return redirect(url_for('auth.unconfirmed'))


# 更新已登录用户的访问时间
@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.': return redirect(url_for('auth.unconfirmed'))


# 重定向到 /auth/unconfirmed 路由，显示一个确认账户 相关信息的页面。

@auth.route('/unconfirmed') def unconfirmed():
    if current_user.is_anonymous() \
            or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


# 如果 before_request 或 before_app_request 的回调返回响应或重定向，
# Flask 会直接将其发送至客户端，而不会调用请求的视图函数。
# 因此，这些回调可 在必要时拦截请求。

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


# 个人资料页面(包含博客文章)路由
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


# 编辑个人资料路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 管理员资料编辑路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    # 使用 Flask-SQLAlchemy 提供的 get_or_404() 函数，如果提供的 id 不正确，则会返回 404 错误
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

#新建文章和文章列表(+分页)路由
@main.route('/aritcle', methods=['GET', 'POST'])
def article():
    form = PostForm()
    #在发布新文章之前，要检查当前用户是否有写文章的权限
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        #把表单和完整的博客文章列表传给模板
        post = Post(body=form.body.data,
        author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # 渲染的页数从请求的查询字符串(request.args)中获取
    page = request.args.get('page', 1, type=int)
    # 文章列表按照时间戳进行降序排列
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    #显示某页中记录， all() -> Flask-SQLAlchemy 提供的 paginate() 方法
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    return render_template('index.html', form=form, posts=posts,pagination=pagination)
    # 必选参数 page=页数
    # 可选参数per_page=每页显示的记录数量,默认显示 20 个记录,从程序的环境变量 FLASKY_POSTS_PER_PAGE 中读取
    # 可选参数为 error_ out=True (默认值)请求页数超出了范围 404 错误;
    # error_ out=False，页数超出范围时会返回一个空列表
    # 第2页文章 URL?page=2

