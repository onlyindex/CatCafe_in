from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request, session
from db import get_db
from app.auth import login_required

user_bp = Blueprint('user', __name__, url_prefix='/user')


# 用户资料
@user_bp.route('/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select username,about_me from user '
                   'where user_id = %s ' % user_id)
    user = cursor.fetchall()
    return render_template('user/user.html', user=user)


# 用户评论、点赞展示


# 个人资料
@login_required
@user_bp.route('/profile', methods=['GET'])
def my_profile():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select username,about_me from user '
                   'where user_id = %s ' % user_id)
    user = cursor.fetchone()
    return render_template('user/user.html', user=user)


# 更新个人资料
@login_required
@user_bp.route('/profile_edit', methods=['GET', 'POST'])
def edit_my_profile():
    user_id = session['user_id']
    if request.method == 'POST':
        about_me = request.form['about_me']
        if not about_me:
            flash('个人资料不为空', 'warning')
            return render_template('user/user_edit.html')
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("update user set about_me = '%s' "
                           " where user_id = %s " % (about_me, user_id))
            db.commit()
            flash('更新个人资料成功', 'info')
            return redirect(url_for('user.my_profile'))
    return render_template('user/user_edit.html')

# 个人资料页日志数、被喜欢数 被评论数展示
