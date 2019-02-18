from flask import Blueprint, render_template, redirect, request, url_for, flash,  g
from db import get_db
from werkzeug.exceptions import abort
from app.auth import login_required

post_bp = Blueprint('post', __name__, url_prefix='/post')


# 日志列表
@post_bp.route('/index', methods=['GET'])
def index():
    if request.method == 'GET':
        error = None
        db = get_db()
        posts = db.execute('select p.id,p.title,p.body,p.created,p.author_id,u.username'
                           'from post as p join user as u on p.author_id = u.id'
                           ' order by p.created desc').fetchall()
        if posts is None:
            error = "喵喵喵啥日志也没有(￣o￣) . z Z"
            flash(error)
    return render_template('post/index.html', posts=posts)


# 新建日志
@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = '标题不能为空'
        elif not body:
            error = '内容不能为空'
        else:
            db = get_db()
            db.execute('insert into post (title,body,author_id)'
                       'values(?,?,?)', (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('post.index'))
        flash(error)
    return render_template('post/create.html')


# 修改or删除日志 先定义 get_post(id)操作
def get_post(id, check_author=True):
    post = get_db().execute('select p.id,title,body,created,author_id,username'
                            'from post p join user u on p.author_id=u.id'
                            'where p.id=?', (id,)).fetchone()
    if post is None:
        abort(404, 'Post id{0} 不存在'.format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post
# 401 Unauthorized redirect(login)


# 日志详情
@post_bp.route('/<int:id>', methods=['GET'])
def post(id):
    post = get_post(id)
    if request.method == 'GET':
        return render_template('post/_post.html', post=post)


# 修改 vs 新建  修改使用日志对象 update->insert
# 修改日志
@post_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['post']
        error = None
        if not title:
            error = '标题不为空'
        elif not body:
            error = '内容不为空'
        else:
            db = get_db()
            db.execute('update post set title=?,body=?'
                       'where id = ?',
                       (title, body, id))
            db.commit()
            return redirect(url_for('post.index'))
        flash(error)
        return render_template('post/update.html', post=post)


# 删除日志
@post_bp.route('<int:id>/delete', methods=['POST', ])
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('delete from post where id=?', (id,))
    db.commit()
    return redirect(url_for('post.index'))
# url_for('post.update', id=post['id'])
