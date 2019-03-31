from flask import Blueprint, render_template, redirect, request, url_for, flash,  g
from db import get_db
from werkzeug.exceptions import abort
from app.auth import login_required

post_bp = Blueprint('post', __name__, url_prefix='/post')


# 动态日志页
@post_bp.route('/', methods=['GET'])
def home():pass








# 日志列表
@post_bp.route('/index', methods=['GET'])
def index():
    if request.method == 'GET':
        error = None
        db = get_db()
        posts = db.execute('select p.post_id, p.post_title, p.post_body, datetime(p.post_timestamp) as post_timestamp,u.username '
                           'from post as p '
                           'join user as u '
                           'on p.author_id = u.user_id order by p.post_timestamp desc').fetchall()
        if posts is None:
            error = "喵喵喵啥日志也没有(￣o￣) . z Z"
            flash(error, 'warning')
    return render_template('post/index.html', posts=posts)


# 新建日志
@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags = request.form['tags']
        tag_name = [str(tag_name) for tag_name in tags.split()]
        error = None
        if not title:
            error = '标题不能为空'
        elif not body:
            error = '内容不能为空'
        else:
            db = get_db()
            for tag in tag_name:
                if db.execute('select tag_id from tag where tag_name = ?', (tag,)).fetchone() is None:
                    db.execute('insert into tag(tag_name) values(?)', (tag,))

            db.execute('insert into post (post_title,post_body,author_id) values(?,?,?)', (title, body, g.user['user_id']))


            db.commit()
            return redirect(url_for('post.index'))
        flash(error)
    return render_template('post/create.html')


# 修改or删除日志 先定义 get_post(post_id)操作
def get_post(post_id, check_author=True):
    post = get_db().execute('select * '
                            'from post as p '
                            'join user as u '
                            'on p.author_id = u.user_id where p.post_id=?', (post_id, )
                            ).fetchone()
    if post is None:
        abort(404, 'Post p.post_id{0} 不存在'.format(id))
    if check_author and post['author_id'] != g.user['user_id']:
        abort(403)
    return post
# 401 Unauthorized redirect(login)


# 日志详情
@post_bp.route('/<int:post_id>', methods=['GET'])
def post(post_id):
    post = get_post(post_id)
    if request.method == 'GET':
        return render_template('post/post.html', post=post)


# 修改 vs 新建  修改使用日志对象 update->insert
# 修改日志
@post_bp.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update(post_id):
    post = get_post(post_id)
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
            db.execute('update post set post_title=?,post_body=?'
                       'where post_id = ?',
                       (title, body, post_id))
            db.commit()
            return redirect(url_for('post.index'))
        flash(error)
        return render_template('post/update.html', post=post)


# 删除日志
@post_bp.route('<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    get_post(post_id)
    db = get_db()
    db.execute('delete from post where post_id=?', (post_id,))
    db.commit()
    return redirect(url_for('post.index'))
# url_for('post.update', post_id=post['post_id'])


# [post页面] get请求 某日志评论总数  按照时间倒叙排列的评论列表
@post_bp.route('/<int:post_id>', methods=['GET'])
def post_comment_index(post_id):
    db = get_db()
    count = db.execute('select count(*) '
                       'from comment as c '
                       'where c.post_id = ?', (post_id,)).fetchone()
    comments = db.execute(
        'select c.comment_body, datetime(c.comment_timestamp) as comment_timestamp,u.username '
        'from comment as c '
        'where c.post_id = ?',
        'join user as u '
        'on c.reader_id = u.user_id '
        'order by comment.comment_timestamp desc', (post_id,)).fetchall()
    return render_template('post/post.html', comments=comments, count=count)


# post请求处理提交评论评论失败or成功 重定向or重新渲染文章详情页
@post_bp.route('/<int:post_id>', methods=['POST'])
@login_required
def post_comment_add(post_id):
    if request.method == 'POST':
        body = request.form['body']
        error = None
        if not body :
            error='评论不能为空'
        else:
            db = get_db()
            db.execute('insert into comment (comment_body,reader_id,post_id)'
                       'values(?,?,?)', (body, g.user['user_id'], post_id))
            db.commit()
            return redirect(url_for('post.post_comment_index', post_id=post_id))
        flash(error)
    return render_template('post/post.html')
