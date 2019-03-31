from flask import Blueprint, request, session, redirect, flash, render_template, url_for
from werkzeug.security import check_password_hash
from db import get_db


admin_bp = Blueprint('admin', __name__, url_prefix='admin')
# 项目超级大多人协作不同模块每个模块下都包含/static/ 比如/admin/static_admin/
# static_folder='static_admin'  访问static_admin目录下的静态文件
# static_url_path='/lib'  将为 static_admin 文件夹的路由设置为 /lib
# template_folder='templates' 每个模块下都包含/templates/


@admin_bp.route('/signin', methods=['GET', 'POST'])
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
        flash(error, 'warning')
    return render_template('auth/signin.html')


@admin_bp.route('/signout')
def signout():
    session.clear()
    flash('success signout', 'success')
    return redirect(url_for('admin.signin'))


@admin_bp.route('/page/')
def pages():
    pass


@admin_bp.route('/page/new/')
def new_page():
    pass


@admin_bp.route('/page/edit')
def edit_page():
    pass


@admin_bp.route('/page/delete')
def delete_page():
    pass






