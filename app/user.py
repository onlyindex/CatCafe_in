from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request, session
from db import get_db
from app.auth import login_required

user_bp = Blueprint('user', __name__, url_prefix='/user')


# 用户资料
@user_bp.route('/<int:user_id>', methods=['GET'])
def user_profile(user_id):
        db = get_db()
        user = db.execute('select username,about_me from user '
                          'where user_id = %s ' % (user_id,)).fetchall()
        return render_template('user/user.html', user=user)


# 个人资料
@user_bp.route('/profile', methods=['GET'])
@login_required
def my_profile():
    user_id = session['user_id']
    db = get_db()
    user = db.execute('select username,about_me from user '
                      'where user_id = s% ' % (user_id,)).fetchone()
    return render_template('user/user.html', user=user)


# 更新个人资料
@user_bp.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def edit_my_profile():
    user_id = session['user_id']
    if request.method == 'POST':
        about_me = request.form['about_me']
        if not about_me:
            flash('个人资料不为空', 'warning')
            return render_template('user/user_edit.html')
        else:
            db = get_db()
            db.execute('update user set about_me =?'
                       ' where user_id = s% ' % (about_me, user_id))
            db.commit()
            flash('更新个人资料成功', 'info')
            return redirect(url_for('user.my_profile'))
    return render_template('user/user_edit.html')
