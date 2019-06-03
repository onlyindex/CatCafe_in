from flask import Blueprint, request, session, render_template, redirect, url_for, flash
from db import get_db
from app.post import get_post_basic, get_post_tags
from app.auth import admin_login_required

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
@admin_login_required
@admin_bp.route('/post/manage', methods=['GET'])
def manage_post():
    # 查询所有文章、进行分页处理?、传入模板
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select p.post_id,p.post_title,timestamp(p.post_timestamp) as post_timestamp,p.author_alias '
                   'from post as p '
                   'order by p.post_timestamp desc ')
    posts = cursor.fetchall()
    return render_template('admin/post_manage.html', posts=posts)


# No.= post_id=post[0],Title=post_title=post[1],Date=post_timestamp=post[2],Alias=author_alias=post[3],
# 增加Tags 和 Comments 两个属性

# 发布草稿
@admin_login_required
@admin_bp.route('post/new', methods=['GET', 'POST'])
def draft_post(post_id):
    db = get_db()
    # 草稿状态  set post_status="draft"
    return redirect(url_for('admin.'))


# 发布日志
@admin_login_required
@admin_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags = request.form['tags']
        alias = request.form['alias']
        # 分割tags获得一组字符串['a','b']
        tag_name = [str(tag_name) for tag_name in tags.split()]
        user_id = session['user_id']
        error = None
        tag_ids = []

        if not title:
            error = '标题不能为空'
        elif not body:
            error = '内容不能为空'
        elif not tags:
            error = '标签不为空'
        elif not alias:
            error = '别名不能为空'
        else:
            db = get_db()
            cursor = db.cursor()
            for tag in tag_name:
                cursor.execute("select tag_id from tag where tag_name = '%s' " % tag)
                if cursor.fetchone() is None:
                    # 查询tag判断其是否在数据中已经存在，如果不存在就添加tag，存在就默认不添加
                    cursor.execute("insert into tag(tag_name) values('%s') " % tag)
                    cursor.execute("select tag_id from tag where tag_name = '%s'" % tag)
                    # tag_ids = tag_ids.insert(0, cursor.fetchone()[0])

            # 查询该文章所有tag_id
            cursor.execute("select t.tag_id from tag as t where tag_name in (%s) " % ','.join(['%s'] * len(tag_name)),
                           tag_name)
            tag_ids = cursor.fetchall()

            # 添加post
            cursor.execute(
                "insert into post(post_title,post_body,author_id,author_alias) values('%s','%s',%s,'%s') " % (
                    title, body, user_id, alias))
            # 获得最新新生成的post_id
            cursor.execute("select max(post_id) from post WHERE author_id= '%s' " % user_id)
            post_id = cursor.fetchone()
            # 更新user表中的别名_(:зゝ∠)_判断别名是否已经存在在，再进行更新
            # 把发布日志中的别名。
            # 关联表 没有更新成功
            if tag_ids is not None:
                for tag_id in tag_ids:
                    cursor.execute(
                        "insert into r_post_by_tag(post_id,tag_id) values (%s,%s) " % (post_id[0], tag_id[0]))
            db.commit()
            flash('发布成功', 'info')
            return redirect(url_for('admin.manage_post'))
        flash(error, 'warning')
    return render_template('admin/post_new.html')


# 新建日志新建标签时候选选择旧标签通过tag——name关联旧的tag——id
# 更新日志更新标签时候先选择旧标签（先搜索tag——name的tag——id）通过tag——name更新旧的tag——id，如果tag——name为新则按照添加新的标签处理add tagname和tag——id


# 修改 vs 新建  修改使用日志对象 update->insert
# 修改日志
@admin_login_required
@admin_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = get_post_basic(post_id)
    tags = get_post_tags(post_id)
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
            db.cursor().execute('update post set post_title= %s ,post_body= %s '
                                'where post_id = %s ' % (title, body, post_id))
            db.commit()
            return redirect(url_for('admin.manage_post'))
        flash(error)
        return render_template('admin/post_edit.html', post=post)


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
@admin_bp.route('<int:post_id>/renew', methods=['GET', 'POST'])
def renew_post(post_id):
    db = get_db()
    # 删除不要真的删除而是搞个隐藏标记
    db.cursor().execute("update post set post_status='display' "
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
    cursor.execute('select u.username,timestamp(c.comment_timestamp) as comment_timestamp,c.comment_body, '
                   'from comment as c and user as u '
                   'where c.reader_id=u.user_id ')
    comments = cursor.fetchall()
    return render_template('admin/post_manage.html', comments=comments)

# 后台回复评论  跟发布新评论好像？