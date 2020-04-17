from flask import Blueprint, render_template,request
from db import get_db
from app.auth import login_required

msg_bp = Blueprint('post', __name__, url_prefix='/msg')


# [message页面] get方法获得所有日志相应用户的所有评论
@login_required
@msg_bp.route('/message', methods=['GET'])
def message():
    if request.method == 'GET':
        db = get_db()
        count = db.execute('select count(*) '
                           'from comment ').fetchone()
        comments = db.execute(
            'select c.comment_body, datetime(c.comment_timestamp) as comment_timestamp,u.username '
            'from comment as c '
            'join user as u '
            'on c.reader_id = u.user_id '
            'order by comment.comment_timestamp desc').fetchall()
    return render_template('message/message.html', comments=comments, count=count)


