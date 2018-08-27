from os import abort

from flask import render_template, flash, url_for, app
from permission import Permission
from sqlalchemy.sql.functions import current_user
from werkzeug.utils import redirect

from app import db
from app.forms import EditProfileForm, EditProfileAdminForm
from app.models import User, Role, Post
from decorators import permission_required, admin_required

'''
# resume 开发后期新建一个简历页面并在个人资料页附上简历链接
@app.route('/resume')
def resume():
    return 'resume'
'''

@app.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@app.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


# 个人资料页面(包含博客文章)路由
# '{}\'s profile'.format(username)
@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

# 编辑个人资料路由
@app.route('/edit-profile', methods=['GET', 'POST'])
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
@app.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
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
