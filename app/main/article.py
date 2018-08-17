# 创建博客蓝图

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, abort

from werkzeug.exceptions import abort
from jinja2 import TemplateNotFound

from app.auth import login_required
from app.db import get_db

# simple_page=bp=article  url_prefix='蓝图位置' 蓝图挂接位置不同蓝图不同   __name__ 这个参数 指定与蓝图相关的逻辑 Python 模块或包
bp = Blueprint('article', __name__, url_prefix='/article')


# @bp.route('/', defaults={'page': 'index'})


# article list
@bp.route('/article')
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




# creat article
@bp.route('/article/create', methods=('GET', 'POST'))
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
@bp.route('/article/<int:id>/update', methods=('GET', 'POST'))
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
@bp.route('/article/<int:id>/delete', methods=('POST',))
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
@bp.route('/article/<int:id>')
def show_article(id):
    try:
        return render_template('/article/%d.html' % id)
    # return 'artilce %d' % a_id
    except TemplateNotFound:
        abort(404)


# article 404
@bp.errorhandler(404)
def page_not_found(e):
    return render_template('/article/404.html')
