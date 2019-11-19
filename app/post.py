from flask import Blueprint, render_template, redirect, request, url_for, flash, g, session
from db import get_db
from werkzeug.exceptions import abort
from app.auth import login_required

post_bp = Blueprint('post', __name__, url_prefix='/post')


# 展示日志列表  先分页再分组再按照日期排序 每页7篇日志
# 获得日志所有分类
@post_bp.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        error = None
        db = get_db()
        # get游标 sqlite3封装了get游标的过程 mysql木有
        cursor = db.cursor()
        cursor.execute(
            'select p.post_id, p.post_title, p.post_timestamp '
            'from post as p '
            'order by post_timestamp desc '
        )
        posts = cursor.fetchall()
        # 获取最终想要的集合
        # execute返回的是执行结果行数

        if posts is None:
            error = "喵喵喵啥日志也没有(￣o￣) . z Z"
            flash(error, 'warning')
            return redirect(url_for('post.index'))
    return render_template('post/locus.html', posts=posts)

# 某分类下的日志列表

# 日志详情页
@post_bp.route('/<int:post_id>', methods=['GET'])
def post(post_id):
    if request.method == 'GET':
        # 获得日志标题+内容+发布时间＋作者
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'select p.post_id,p.post_title,p.post_body,date(p.post_timestamp) as post_timestamp,u.username '
            'from post as p,user as u '
            'where author_id=u.user_id and p.post_id= %s ' % post_id)
        post = cursor.fetchone()
        # cursor.execute('select t.tag_name from (tag as t '
        #                'inner join r_post_by_tag as r on t.tag_id = r.tag_id) '
        #                'inner join post as p on r.post_id = p.post_id '
        #                'where p.post_id = %s ' % post_id)
        # tags = cursor.fetchall()
        if post is None:
            abort(404, 'Post post[0] 不存在'.format(id))
            return post
        else:
            return render_template('post/post.html', post=post)

        # check_author=True
        # if check_author and post['user_id'] != g.user['user_id']:
        #    abort(403)
        # 403 权限不当禁止访问
        # 401 Unauthorized redirect(login)








# 获得 日志评论总数
def post_comment_count(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select count(*) '
                   'from comment as c '
                   'where c.post_id = %s' % (post_id,))
    count = cursor.fetchone()
    return count





# get请求 按照时间倒叙排列的评论列表
@post_bp.route('/<int:post_id>', methods=['GET'])
def post_comment_index(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'select c.comment_body, datetime(c.comment_timestamp) as comment_timestamp,u.username '
        'from comment as c '
        'where c.post_id = s% ',
        'join user as u '
        'on c.reader_id = u.user_id '
        'order by comment.comment_timestamp desc' % (post_id,))
    comments = cursor.fetchall()
    return render_template('post/post.html', comments=comments)


# post请求  提交日志 评论评论
@login_required
@post_bp.route('/<int:post_id>', methods=['POST'])
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

# 前台回复评论 管理员回复