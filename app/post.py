from flask import Blueprint, render_template, redirect, request, url_for, flash, g, session
from db import get_db
from werkzeug.exceptions import abort
from app.auth import login_required
from itertools import  groupby
from operator import  itemgetter

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
            "select p.post_id, p.post_title, date(p.post_timestamp) as post_timestamp, strftime('%Y',p.post_timestamp) as group_name "
            "from post as p "
            "order by post_timestamp desc"
        )

        # fetchone() 返回单个的元组，也就是一条记录(row)，or None
        # fetchall() ：返回多个元组，即返回多个记录(rows), or 返回()

        # return dict={('key':group)}
        rows = cursor.fetchall()
        # 用for循环rows
        #获得多条数据
        # rows=[(1,"titile","2008-05-06",'2008'),,]
        # rows = [ {'fname': 'Brian', 'lname': 'Jones', 'uid': 1003},{'fname': 'David', 'lname': 'Beazley', 'uid': 1002}.,]
        # key="重复的那个内容"
        # goups="相同内容组成的列表"
        # 我通过查找重复的年然后把相同年份的日志组成了一个组列表我需要把处理后的数据以key对应value=group的形式存起来
        group_by_key = {}
        for key,group in groupby(rows, key=itemgetter('group_name')):
            post_list = []
            for post in group:
                post_list.append(post)
            group_by_key[key] = post_list

        # return dict={('key':group)}
        if rows is None:
            error = "喵喵喵啥日志也没有(￣o￣) . z Z"
            flash(error, 'warning')
            return redirect(url_for('post.index'))
    return render_template('post/locus.html', group_by_key=group_by_key)

# 某分类下的日志列表
@post_bp.route('/<catalog_name>', methods=['GET'])
def catalog():
    if request.method == 'GET':
        error = None
        db = get_db()
        # get游标 sqlite3封装了get游标的过程 mysql木有
        cursor = db.cursor()
        cursor.execute(
            'select p.post_id, p.post_title, p.post_timestamp,c.catalog_name '
            'from post as p,catalog as c'
            'where c.catalog_id= %s '
            'order by post_timestamp desc '% catalog_name
        )
        posts = cursor.fetchall()
        # 获取最终想要的集合
        # execute返回的是执行结果行数

        if posts is None:
            error = "喵喵喵啥日志也没有(￣o￣) . z Z"
            flash(error, 'warning')
            return redirect(url_for('post.index'))
    return render_template('post/catalog.html', posts=posts)

# 日志详情页 show_post
@post_bp.route('/<int:post_id>', methods=['GET'])
def post(post_id):
    if request.method == 'GET':
        # 获得日志标题+内容+时间
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'select p.post_id,p.post_title,p.post_body,date(p.post_timestamp) as post_timestamp '
            'from post as p '
            'where p.post_id= %s ' % post_id)
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
            return render_template('post/_post.html', post=post)

        # check_author=True
        # if check_author and post['user_id'] != g.user['user_id']:
        #    abort(403)
        # 403 权限不当禁止访问
        # 401 Unauthorized redirect(login)


# get请求 获取评论列表 对其进行排序和分页处理
@post_bp.route('/<int:post_id>', methods=['GET'])
def post_comment_index(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'select c.comment_id,c.comment_body, datetime(c.comment_timestamp) as comment_timestamp,u.username '
        'from comment as c,user as u '
        'where c.reader_id = u.user_id and c.post_id = %s ' % (post_id,))
    cursor.execute('select count(*) '
                   'from comment as c '
                   'where c.post_id = %s' % (post_id,))
    count = cursor.fetchone()
    comments = cursor.fetchall()
    return render_template('post/_post.html', comments=comments, count=count)


# post请求  提交日志 评论评论
# g.user['user_id']
@login_required
@post_bp.route('/<int:post_id>', methods=['POST'])
def post_comment_add(post_id):
    if request.method == 'POST':
        body = request.form['body']
        user_id = g.user['user_id']
        if not body:
            flash('评论不能为空', 'warning')
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("insert into comment (comment_body,reader_id,post_id) "
                           "values('%s',%s,%s) " % (body, user_id, post_id))
            db.commit()
            return redirect(url_for('post.post_comment_index', post_id=post_id))
    return render_template('post/_post.html')

# 前台回复评论 管理员回复