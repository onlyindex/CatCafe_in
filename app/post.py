from flask import Blueprint, render_template, redirect, request, url_for, flash, g, session
from db import get_db
from werkzeug.exceptions import abort
from app.auth import login_required

post_bp = Blueprint('post', __name__, url_prefix='/post')


# 展示首页动态 从post和user获得post_title,post_timestamps,username,order by timestamps
@post_bp.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        error = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'select p.post_id, p.post_title, date(p.post_timestamp) as post_timestamp,p.author_alias,p.author_id '
            'from post as p  '
            'order by p.post_timestamp desc ')
        posts = cursor.fetchall()
    return render_template('home.html', posts=posts)


# 展示日志列表  先分页再分组再按照日期排序
@post_bp.route('/index', methods=['GET'])
def index():
    if request.method == 'GET':
        error = None
        db = get_db()
        # get游标 sqlite3封装了get游标的过程 mysql木有
        cursor = db.cursor()
        cursor.execute(
            'select p.post_id, p.post_title, timestamp(p.post_timestamp) as post_timestamp,p.author_alias '
            'from post as p '
            'order by post_timestamp desc '
        )
        # execute返回的是执行结果行数
        posts = cursor.fetchall()
        # 获取最终想要的集合
        if posts is None:
            error = "喵喵喵啥日志也没有(￣o￣) . z Z"
            flash(error, 'warning')
            return redirect(url_for('post.index'))
    return render_template('post/index.html', posts=posts)


# 获得日志详细信息
# 修改or删除日志 先定义 get_post(post_id)操作
def get_post(post_id):
    db = get_db()
    cursor = db.cursor()
    # join alisa as a  on p.alias = a.alias
    # 获得日志相关信息
    cursor.execute(
        'select p.post_id,p.post_title,p.post_body,date(p.post_timestamp) as post_timestamp,p.author_alias '
        'from post as p '
        'where p.post_id= %s ' % post_id)
    post = cursor.fetchone()
    if post is None:
        abort(404, 'Post post[0] 不存在'.format(id))
        # 放弃在前台检查是否是当前文章的用户给编辑等其他权限
        # check_author=True
    # if check_author and post['user_id'] != g.user['user_id']:
    #    abort(403)
    return post


# 403 权限不当禁止访问
# 401 Unauthorized redirect(login)
# 获得日志标签
def get_post_tag(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select t.tag_name from (tag as t '
                   'inner join r_post_by_tag as r on t.tag_id = r.tag_id) '
                   'inner join post as p on r.post_id = p.post_id '
                   'where p.post_id = %s ' % post_id)
    tags = cursor.fetchall()
    print(tags)
    return tags


# 展示日志详情
@post_bp.route('/<int:post_id>', methods=['GET'])
def post(post_id):
    post = get_post(post_id)
    tags = get_post_tag(post_id)
    return render_template('post/post.html', post=post, tags=tags)


# get请求展示某日志评论总数  按照时间倒叙排列的评论列表
@post_bp.route('/<int:post_id>', methods=['GET'])
def post_comment_index(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select count(*) '
                   'from comment as c '
                   'where c.post_id = %s' % (post_id,))
    count = cursor.fetchone()
    cursor.execute(
        'select c.comment_body, datetime(c.comment_timestamp) as comment_timestamp,u.username '
        'from comment as c '
        'where c.post_id = s% ',
        'join user as u '
        'on c.reader_id = u.user_id '
        'order by comment.comment_timestamp desc' % (post_id,))
    comments = cursor.fetchall()
    return render_template('post/post.html', comments=comments, count=count)


# post请求  提交日志 评论评论
@post_bp.route('/<int:post_id>', methods=['POST'])
@login_required
def post_comment_add(post_id):
    if request.method == 'POST':
        body = request.form['body']
        error = None
        if not body:
            error = '评论不能为空'
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("insert into comment (comment_body,reader_id,post_id)"
                           "values('%s',%s,%s)" % (body, g.user['user_id'], post_id))
            db.commit()
            return redirect(url_for('post.post_comment_index', post_id=post_id))
        flash(error)
    return render_template('post/post.html')
