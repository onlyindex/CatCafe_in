from flask import Blueprint, request, session, render_template, redirect, url_for, flash, make_response, abort, \
    current_app
from db import get_db
from app.auth import login_required
import json
import random
import urllib
import datetime
from itertools import groupby
from operator import itemgetter
from app.utiles import redirect_back
from werkzeug import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 项目超级大多人协作不同模块每个模块下都包含/static/ 比如/admin/static_admin/
# static_folder='static_admin'  访问static_admin目录下的静态文件
# static_url_path='/lib'  将为 static_admin 文件夹的路由设置为 /lib
# template_folder='templates' 每个模块下都包含/templates/


# 后台首页
@login_required
@admin_bp.route('/', methods=['GET'])
def dashboard():
    # 查询3天内草稿
    # 查询3天内文章数据统计
    return render_template('admin/dashboard.html')


# 日志管理
# mysql->sqlite timstamp
@login_required
@admin_bp.route('/post/manage', methods=['GET'])
def manage_post():
    # 查询所有文章、进行分页处理?、传入模板
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'select p.post_id,p.post_title,date(p.post_timestamp) as post_timestamp,p.post_status,c.catalog_name '
        'from post as p,catalog as c '
        'where p.catalog_id = c.catalog_id '
        'order by p.post_timestamp desc ')
    posts = cursor.fetchall()
    return render_template('admin/post_manage.html', posts=posts)


# 发布日志
@login_required
@admin_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        status = request.form['status']
        collection_name = request.form['collecion_name']
        print(collection_name)
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
        elif not collection_name:
            error = " 必须选择文集 "
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
                "insert into post(post_title,post_body,post_status,author_id,collection_name) "
                "values('%s','%s','%s',%s,%s)" % (title, body, status, user_id, collection_name))
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
@login_required
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
@login_required
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
@login_required
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
# @login_required
# @admin_bp.route('/tag/manage', methods=['GET'])
# def manage_tag():
#     return render_template('admin/tag_manage.html')


# 文集管理
@login_required
@admin_bp.route('/collection/manage', methods=['GET'])
def manage_collection():
    # 列出所有分类
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select c.collection_name,c.collection_img ,c.collection_post_total '
                   'from collection as c ')
    collections = cursor.fetchall()
    return render_template('admin/collection_manage.html', collections=collections)


# 增加文集
@login_required
@admin_bp.route('/collection/new', methods=['GET', 'POST'])
def new_collection():
    if request.method == 'POST':
        collection_name = request.form['collection_name']
        collection_img = request.form['collection_img']
        if not collection_name:
            error = "文集名不能为空"
        elif not collection_img:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "insert into collection(collection_name) values('%s') " % (
                    collection_name))
            db.commit()
            return redirect(url_for('admin.manage_collection'))

        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "insert into collection(collection_name,collection_name) values('%s','%s') " % (
                    collection_name, collection_img))
            db.commit()
            return redirect(url_for('admin.manage_collection'))
        flash(error, 'warning')
    return render_template('admin/collection_new.html')


# 添加文集图片
# @login_required
# @admin_bp.route('/upload/', methods=['GET', 'POST'])
# def upload():
#     # 从媒体库图片列表中选择 or 自己上传图片
# return'图片'


# 媒体管理
@login_required
@admin_bp.route('/file/manage', methods=['GET', 'POST'])
def manage_file():
    # 展示图片列表、视频列表、音频列表
    return render_template('admin/file_manage.html')


# 图片上传
@login_required
@admin_bp.route('/uploads/images/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST' and 'file' in request.files:
        # 如果请求类型为POST，说明是文件上传请求
        #获取图片文件对象f
        f = request.files.get('collection_image')
        # for f in request.files.getlist('file_image') 图片列表
        # 获得图片文件的新名字
        filename = secure_filename(f.filename)

        # 检查图片文件是否存在 确保字段中包含文件数据＝FIleRequired验证器 check_file() check_image()
        if not check_image(f):
            return ''， 400


        # 验证图片文件格式＝FileAllowed  allowed_file() allowed_image()
             

         f.filename.split('.')[1] != 'png':


        # 检查后才可以保存到服务器
        # 保存图片
        f.save(os.path.join(app.config['ALBUMY_UPLOAD_PATH'], filename))
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "insert into photo(photo_name,collection_name) values('%s','%s') " % (
                collection_name, collection_img))
        db.commit()
        return redirect(url_for('admin.manage_collection'))

        flash('upload sucess')
        # session中将文件名保存在
        session['filenames'] = [filename]


filename = session.get('filename')

return redirect(url_for('show_images'))
    return render_template('uplpad.html', file=file)
return render_template('upload.html',filename=filename)


# 展示图片文件
def show_images():

# 检查图片文件是否存在
def check_images():
    # if f not in request.files:
    f = request.files.get('file_image')
    if f is None:
        flash('this image is required')
        return redirect(url_for('admin.upload'))
    else:
        return f





# 评论管理、批准评论、关闭评论
@login_required
@admin_bp.route('/comment/manage', methods=['GET'])
def manage_comment():
    # 分页处理?
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "select p.post_id, p.post_title, u.username,c.comment_id,c.comment_body,date(c.comment_timestamp) as comment_timestamp, strftime('%Y-%m-%d',c.comment_timestamp) as group_name "
        "from post as p,user as u,comment as c "
        "where c.post_id=p.post_id and c.reader_id=u.user_id "
        "order by comment_timestamp desc "
    )
    rows = cursor.fetchall()
    # 返回分组的多行数据
    # 新建key group 的空字典 利用key=groupname然后分组cm_list=group
    # 再遍历cm把cm存到cm_list
    group_by_key = {}
    for key, cm_list in groupby(rows, key=itemgetter('group_name')):
        group = []
        for comment in cm_list:
            group.append(comment)
        group_by_key[key] = group
    if rows is None:
        error = "喵喵喵啥评论也没有(￣o￣) . z Z"
        flash(error, 'warning')
        return redirect(url_for('admin.manage_comment'))
    return render_template('admin/comment_manage.html', group_by_key=group_by_key)


# 回复评论
@login_required
@admin_bp.route('/comment/manage', methods=['GET'])
def reply_commnet():
    return ''


# 后台回复评论  跟发布新评论好像？


# 分类管理
@login_required
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
@login_required
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


# 读者管理
@login_required
@admin_bp.route('/user/manage', methods=['GET', 'POST'])
def manage_user():
    if request.method == 'GET':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'select u.user_id,u.username '
            'from user as u ')
    users = cursor.fetchall()
    return render_template('admin/user_manage.html', users=users)


@login_required
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


# 主题切换入口
@login_required
@admin_bp.route('/theme/')
def theme():
    # 手动添加if语句判断url变量中的主题名称在支持范围 出错返回404
    # if theme_name not in current_app.config['THEMES'].keys():
    # abort(404)
    # 重定向原来页面除非找不到返回后台首页 form 辅助函数utils.py
    # response = make_response(admin_redirect_back())
    # 将主题名称保存在名为theme的cookie中 cookie过期时间30天
    # response.set_cookie('theme', 'theme_name', max_age=30*24*60*60)
    # 加载主题选项值储存在客户端cookie中
    return render_template('admin/change_theme.html')


# 切换主题
# 或者在url规则里使用any转换器 url规则中无法使用current_app 可以写死可选值 太不灵活
# @admin_bp.route('change_theme/<any(Pink,Blue):theme_name>')
# 直接从setting模块导入['THEMES']构建正确的选项字符串
# @admin_bp.route('change_theme/<any(%s):theme_name>' % str（['THEMES'].keys())[1:-1]) 太麻烦
@login_required
@admin_bp.route('/theme/<string:theme_name>')
def change_theme(theme_name):
    # 手动添加if语句判断url变量中的主题名称在支持范围 出错返回404
    if theme_name not in current_app.config['THEMES'].keys():
        abort(404)
        # 重定向原来页面除非找不到返回后台首页 form 辅助函数utils.py
    response = make_response(redirect_back())
    # 将主题名称保存在名为theme的cookie中 cookie过期时间30天
    response.set_cookie('theme', 'theme_name', max_age=30 * 24 * 60 * 60)
    # 加载主题选项值储存在客户端cookie中
    return render_template('admin/change_theme.html')
