from flask_mail import Message

# 定义邮件主题的前缀和发件人的地址
from flask import session, render_template, redirect

from app.main import email, app
from app.main.forms import SignupForm
from app.models import User
from threading import Thread

# 异步返送电子邮件
def send_async_email(app, msg):
    with app.app_context():
        email.send(msg)


def send_email(to, subject, template, **kwargs):
    # 收件人地址、主题、渲染邮件正文的模板和关键字参数列表
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    email.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

# 指定 模板时不能包含扩展名，这样才能使用两个模板分别渲染纯文本正文和富文本正文。

@app.main.route('/', methods=['GET', 'POST'])
def confirm_mail():
    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
            session['name'] = form.name.data
            form.name.data = ''
            return redirect(url_for('index'))
        return render_template('index.html', form=form, name=session.get('name'),
                               known=session.get('known', False))
# 表单接收新名字时，程序都会给管理员发送一 封电子邮件

