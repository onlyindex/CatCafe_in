from flask import Blueprint, request, render_template, redirect, url_for, flash
from db import get_db
from app.post import get_post, get_post_tag
from app.auth import login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
# 项目超级大多人协作不同模块每个模块下都包含/static/ 比如/admin/static_admin/
# static_folder='static_admin'  访问static_admin目录下的静态文件
# static_url_path='/lib'  将为 static_admin 文件夹的路由设置为 /lib
# template_folder='templates' 每个模块下都包含/templates/


@admin_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template('admin/dashboard.html')


@admin_bp.route('/post/manage', methods=['GET'])
@login_required
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
# 新建日志
@admin_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
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
            cursor.execute("select t.tag_id from tag as t where tag_name in (%s) " % ','.join(['%s']*len(tag_name)),
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
                    cursor.execute("insert into r_post_by_tag(post_id,tag_id) values (%s,%s) " % (post_id[0], tag_id[0]))
            db.commit()
            flash('发布成功', 'info')
            return redirect(url_for('post.index'))
        flash(error, 'warning')
    return render_template('admin/post_new.html')
# 新建日志新建标签时候选选择旧标签通过tag——name关联旧的tag——id
# 更新日志更新标签时候先选择旧标签（先搜索tag——name的tag——id）通过tag——name更新旧的tag——id，如果tag——name为新则按照添加新的标签处理add tagname和tag——id


# 修改 vs 新建  修改使用日志对象 update->insert
# 修改日志
@admin_bp.route('/<int:post_id>/update', methods=['GET', 'POST'])
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
            db.cursor().execute('update post set post_title= %s ,post_body= s% '
                                'where post_id = %s ' % (title, body, post_id))
            db.commit()
            return redirect(url_for('post.index'))
        flash(error)
        return render_template('post/post_edit.html', post=post)


# 删除日志
@admin_bp.route('<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    get_post(post_id)
    db = get_db()
    db.cursor().execute('delete from post where post_id= %s' % post_id)
    db.commit()
    return redirect(url_for('post.index'))


# url_for('post.update', post_id=post['post_id'])






# 标签管理
# @admin_bp.route('/tag/<int:tag_id>/delete')
# @login_required


# 评论管理、批准评论、关闭评论



