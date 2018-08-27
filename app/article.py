from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from werkzeug.exceptions import abort
from jinja2 import TemplateNotFound

from app.auth import login_required
from db import get_db


# article list
@app.route('/article')
def show_article_list():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('article/index.html', posts=posts)


# 通过 id 来获取一个 post ，并且 检查作者与登录用户是否一致 打包函数 在每个视图中调用
def get_post(id, check_author=True):
    """Get a post and its author by id.
        Checks that the id exists and optionally that the current user is
        the author.
        :param id: id of post to get
        :param check_author: require the current user to be the author
        :return: the post with author information
        :raise 404: if a post with the given id doesn't exist
        :raise 403: if the current user isn't the author
        """
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# 新建文章和文章列表(+分页)路由
@app.route('/aritcle', methods=['GET', 'POST'])
def article():
    form = PostForm()
    # 在发布新文章之前，要检查当前用户是否有写文章的权限
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        # 把表单和完整的博客文章列表传给模板
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # 渲染的页数从请求的查询字符串(request.args)中获取
    page = request.args.get('page', 1, type=int)
    # 文章列表按照时间戳进行降序排列
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    # 显示某页中记录， all() -> Flask-SQLAlchemy 提供的 paginate() 方法
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    return render_template('index.html', form=form, posts=posts, pagination=pagination)
    # 必选参数 page=页数
    # 可选参数per_page=每页显示的记录数量,默认显示 20 个记录,从程序的环境变量 FLASKY_POSTS_PER_PAGE 中读取
    # 可选参数为 error_ out=True (默认值)请求页数超出了范围 404 错误;
    # error_ out=False，页数超出范围时会返回一个空列表
    # 第2页文章 URL?page=2


# creat article
@app.route('/article/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('article.index'))

    return render_template('article/create.html')


# update article
@app.route('/article/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('article.index'))

    return render_template('article/update.html', post=post)


# url_for('article.update', id=post['id']
# update 视图使用了一个 post 对象和一个 UPDATE 查询代替了一个 INSERT 查询。
# delete article
@app.route('/article/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a post.
        Ensures that the post exists and that the logged in user is the
        author of the post.
        """
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('article.index'))


# article by id
@app.route('/article/<int:id>')
def show_article(id):
    try:
        return render_template('/article/%d.html' % id)
    # return 'artilce %d' % a_id
    except TemplateNotFound:
        abort(404)
