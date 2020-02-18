from flask import Blueprint, render_template, redirect, request, url_for, flash, g, session
from db import get_db
from werkzeug.exceptions import abort
from app.auth import admin_login_required
from itertools import groupby
from operator import itemgetter

post_bp = Blueprint('post', __name__, url_prefix='/post')


# 日志列表  先分页再分组再按照日期排序 每页7篇日志
@post_bp.route('/', methods=['GET'])
def posts():
    if request.method == 'GET':
        error = None
        db = get_db()
        # get游标 sqlite3封装了get游标的过程 mysql木有
        cursor = db.cursor()
        cursor.execute(
            "select p.post_id, p.post_title, date(p.post_timestamp) as post_timestamp, strftime('%Y-%m-%d',p.post_timestamp) as group_name "
            "from post as p "
            "order by post_timestamp desc "
        )
        # fetchone() 返回单个的元组，也就是一条记录(row)，or None
        # fetchall() ：返回多个元组，即返回多个记录(rows), or 返回()
        rows = cursor.fetchall()
        # 用for循环rows=[key,group] 封装成一个词典
        # key=2008 D[2008]=group=[(1,"titile","2008-05-06",'2008'),(2,"titile2","2008-05-07",'2008'),]
        # 我通过查找重复的年然后把相同年份的日志组成了一个组列表
        # 以key对应value=group的形式存起来
        # group里的日志列表也要一条条存起来
        group_by_key = {}
        for key, post_list in groupby(rows, key=itemgetter('group_name')):
            group = []
            for post in post_list:
                group.append(post)
            group_by_key[key] = group
        if rows is None:
            error = "喵喵喵啥日志也没有(￣o￣) . z Z"
            flash(error, 'warning')
            return redirect(url_for('post.posts'))
    return render_template('post/post.html', group_by_key=group_by_key)


# 分类
@post_bp.route('/catalog/', methods=['GET'])
def catalogs():
    if request.method == 'GET':
        error = None
        db = get_db()
        cursor = db.cursor()
        # 获得日志分类和分类统计
        cursor.execute('select c.catalog_name,c.catalog_img ,c.catalog_total from catalog as c')
        catalogs = cursor.fetchall()
    return render_template('post/catalog.html', catalogs=catalogs)


# 分类日志列表
@post_bp.route('/catalog/<catalog_name>', methods=['GET'])
def catalog(catalog_name):
    if request.method == 'GET':
        error = None
        db = get_db()
    #     # get游标 sqlite3封装了get游标的过程 mysql木有
    #     # 其中%Y与python的参数%s冲突 ValueError: unsupported format character ‘Y’ (0x59) at index 70
        cursor = db.cursor()
    #     # 获得某分类下的分类统计
    #     catalog = cursor.execute("select c.catalog_name,c.catalog_total,c.catalog_id "
    #                              "from catalog as c "
    #                              "where c.catalog_name='%s'" % catalog_name).fetchone()
    #
        cursor.execute(
            "select p.post_id, p.post_title, date(p.post_timestamp) as post_timestamp, strftime('%%Y',p.post_timestamp) as group_name "
            "from post as p join catalog as c on c.catalog_id = p.catalog_id "
            "where c.catalog_name='%s' "
            "order by post_timestamp desc" % catalog_name)
        rows = cursor.fetchall()
        group_by_key = {}
        key = itemgetter('group_name')
        for key, group in groupby(rows, key):
            post_list = []
            for post in group:
                post_list.append(post)
            group_by_key[key] = post_list
    #
        if rows is None:
            error = "喵喵喵啥分类也没有(￣o￣) . z Z"
            flash(error, 'warning')
            return redirect(url_for('post.catalog'))
    return render_template('post/_catalog.html', group_by_key=group_by_key)


#tags
@post_bp.route('/tag/', methods=['GET'])
def tags():
    if request.method == 'GET':
        error = None
        db = get_db()
        cursor = db.cursor()
        # 查询所有标签
        cursor.execute('select t.tag_id,t.tag_name,t.tag_total from tag as t')
        tags = cursor.fetchall()
    return render_template('post/tag.html', tags=tags)

#tag

@post_bp.route('/tag_name', methods=['GET'])
def tag():
    if request.method == 'GET':
        return render_template('post/_tag.html')







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


# get请求 获取评论列表 分页？
@post_bp.route('/<int:post_id>', methods=['GET'])
def post_comment_index(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'select c.comment_id,c.comment_body, datetime(c.comment_timestamp) as comment_timestamp,u.username '
        'from comment as c,user as u '
        'where c.reader_id = u.user_id and c.post_id = %s ' % (post_id,))
    comments = cursor.fetchall()
    count = cursor.execute('select count(*) '
                           'from comment as c '
                           'where c.post_id = %s' % (post_id,)).fetchone()
    return render_template('post/_post.html', comments=comments, count=count)


# post请求  提交日志 评论评论
# g.user['user_id']
@admin_login_required
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
