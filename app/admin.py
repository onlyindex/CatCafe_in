from flask import Blueprint, request, session, render_template, redirect, url_for, flash, make_response
from db import get_db
from app.auth import admin_login_required
import re
import json
import random
import urllib
import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 项目超级大多人协作不同模块每个模块下都包含/static/ 比如/admin/static_admin/
# static_folder='static_admin'  访问static_admin目录下的静态文件
# static_url_path='/lib'  将为 static_admin 文件夹的路由设置为 /lib
# template_folder='templates' 每个模块下都包含/templates/


# 后台首页
@admin_login_required
@admin_bp.route('/', methods=['GET'])
def dashboard():
    return render_template('admin/dashboard.html')


# 日志管理
# mysql->sqlite timstamp
@admin_login_required
@admin_bp.route('/post/manage', methods=['GET'])
def manage_post():
    # 查询所有文章、进行分页处理?、传入模板
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select p.post_id,p.post_title,date(p.post_timestamp) as post_timestamp,p.post_status,c.catalog_name '
                   'from post as p,catalog as c '
                   'where p.catalog_id = c.catalog_id '
                   'order by p.post_timestamp desc ')
    posts = cursor.fetchall()
    return render_template('admin/post_manage.html', posts=posts)


# 增加Tags 和 Comments 两个属性


# 发布日志
@admin_login_required
@admin_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        status = request.form['status']
        catalog_id = request.form['catalog_id']
        print(catalog_id)
        # tags = request.form['tags']
        # 分割tags获得一组字符串['a','b']
        # tag_name = [str(tag_name) for tag_name in tags.split()]
        # 从会话信息获取用户id
        user_id = session['user_id']
        error = None
        tag_ids = []

        if not title:
            error = '标题不能为空'
        elif not body:
            error = '内容不能为空'
        # elif not tags:
        #    error = '标签不为空'
        elif not catalog_id:
            error = " 分类不为空 "
        else:
            # for tag in tag_name:
            # cursor.execute("select tag_id from tag where tag_name = '%s' " % tag)
            # if cursor.fetchone() is None:
            #     # 查询tag判断其是否在数据中已经存在，如果不存在就添加tag，存在就默认不添加
            #     cursor.execute("insert into tag(tag_name) values('%s') " % tag)
            #     cursor.execute("select tag_id from tag where tag_name = '%s'" % tag)
            # tag_ids = tag_ids.insert(0, cursor.fetchone()[0])

            # 查询该文章所有tag_id
            # cursor.execute("select t.tag_id from tag as t where tag_name in (%s) " % ','.join(['%s'] * len(tag_name)),
            #                % tag_name)
            # tag_ids = cursor.fetchall()

            # 添加post
            cursor.execute(
                "insert into post(post_title,post_body,post_status,author_id,catalog_id) "
                "values('%s','%s','%s',%s,%s)" % (title, body, status, user_id, catalog_id))
            # 获得最新新生成的post_id
            cursor.execute("select max(post_id) from post WHERE author_id= %s " % user_id)
            # 更新日志分类计数
            cursor.execute("UPDATE catalog SET catalog_total = catalog_total+1 "
                           "where catalog_id=%s " % catalog_id)
            post_id = cursor.fetchone()
            # 更新user表中的别名_(:зゝ∠)_判断别名是否已经存在在，再进行更新
            # 把发布日志中的别名。
            # 关联表 没有更新成功
            # if tag_ids is not None:
            #     for tag_id in tag_ids:
            #         cursor.execute(
            #             "insert into r_post_by_tag(post_id,tag_id) values (%s,%s) " % (post_id[0], tag_id[0]))
            db.commit()
            flash('发布成功', 'info')
            return redirect(url_for('admin.manage_post'))
        flash(error, 'warning')

    cursor.execute('select c.catalog_id,c.catalog_name,c.catalog_img '
                   'from catalog as c ')
    catalogs = cursor.fetchall()

    return render_template('admin/post_new.html', catalogs=catalogs)


# 新建日志新建标签时候选选择旧标签通过tag——name关联旧的tag——id
# 更新日志更新标签时候先选择旧标签（先搜索tag——name的tag——id）通过tag——name更新旧的tag——id，如果tag——name为新则按照添加新的标签处理add tagname和tag——id


# 编辑 vs 新建  修改使用日志对象 update->insert
# 编辑日志
@admin_login_required
@admin_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    # post = get_post_basic(post_id)
    # tags = get_post_tags(post_id)
    if request.method == 'GET':
        db = get_db()
        cursor = db.cursor()
        post = cursor.execute("select post.post_id,post.post_title,post.post_body "
                              "from post "
                              "where post_id= %s" % post_id).fetchone()
        return render_template('admin/post_edit.html', post=post)
    else:
        title = request.form['title']
        body = request.form['body']
        status = request.form['status']
        db = get_db()
        db.cursor().execute("update post set post_title= '%s' ,post_body='%s',post_status='%s' "
                            "where post_id = %s " % (title, body, status, post_id))
        db.commit()
        flash("edit post sucess")
        return redirect(url_for('admin.manage_post'))


# 删除日志
@admin_login_required
@admin_bp.route('<int:post_id>/delete', methods=['GET', 'POST'])
def del_post(post_id):
    db = get_db()
    # 删除不要真的删除而是搞个隐藏标记
    db.cursor().execute("update post set post_status='hide' "
                        "where post_id= %s " % post_id)
    db.commit()
    return redirect(url_for('admin.manage_post'))


# url_for('post.edit', post_id=post['post_id'])


# 恢复日志
@admin_login_required
@admin_bp.route('<int:post_id>/renew', methods=['GET', 'POST'])
def renew_post(post_id):
    db = get_db()
    # 删除不要真的删除而是搞个隐藏标记
    db.cursor().execute("update post set post_status='show' "
                        "where post_id= %s " % post_id)
    db.commit()
    return redirect(url_for('admin.manage_post'))


# 标签管理
# @admin_bp.route('/tag/<int:tag_id>/delete')
# @admin_login_required


# 评论管理、批准评论、关闭评论
@admin_login_required
@admin_bp.route('/comment/manage', methods=['GET'])
def manage_comment():
    # 列出所有用户评论  用户 评论内容 日志 评论时间
    # 分页处理?
    db = get_db()
    cursor = db.cursor()
    # 三表查询 评论表 用户表 日志表
    cursor.execute('select u.username,c.comment_timestamp,c.comment_body,p.post_title '
                   'from comment as c , user as u,post as p '
                   'where c.reader_id=u.user_id and c.post_id=p.post_id ')
    comments = cursor.fetchall()
    return render_template('admin/comment_manage.html', comments=comments)


# 后台回复评论  跟发布新评论好像？


# 分类管理
@admin_login_required
@admin_bp.route('/catalog/manage', methods=['GET'])
def manage_catalog():
    # 列出所有分类
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select c.catalog_name,c.catalog_img ,c.catalog_total '
                   'from catalog as c ')
    catalogs = cursor.fetchall()
    return render_template('admin/catalog_manage.html', catalogs=catalogs)


# 增加分类
@admin_login_required
@admin_bp.route('/catalog/new', methods=['GET', 'POST'])
def new_catalog():
    if request.method == 'POST':
        catalog_name = request.form['catalog_name']
        catalog_img = request.form['catalog_img']
        if not catalog_name:
            error = "catalog 不能为空"
        elif not catalog_img:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "insert into catalog(catalog_name) values('%s') " % (
                    catalog_name))
            db.commit()
            return redirect(url_for('admin.manage_catalog'))

        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "insert into catalog(catalog_name,catalog_img) values('%s','%s') " % (
                    catalog_name, catalog_img))
            db.commit()
            return redirect(url_for('admin.manage_catalog'))
        flash(error, 'warning')
    return render_template('admin/catalog_new.html')


def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@admin_login_required
@admin_bp.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)

        filepath = os.path.join(app.static_folder, 'upload', rnd_name)

        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'

        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'

    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response
