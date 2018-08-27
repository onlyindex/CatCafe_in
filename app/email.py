from wtforms.validators import email

from app.forms import SignupForm, ResetEmailForm
from flask import redirect, url_for, render_template, flash, app
# 定义邮件主题的前缀和发件人的地址
from flask import session
from app.models import User
from sqlalchemy.sql.functions import user, current_user
from app import db
from threading import Thread
from flask_mail import Message

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


# 指定模板时不能包含扩展名，这样才能使用两个模板分别渲染纯文本正文和富文本正文。

@app.route('/', methods=['GET', 'POST'])
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



# 邮箱未认证
@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() \
            or current_user.confirmed:
        return redirect(url_for('index'))
    return render_template('unconfirmed.html')

# 发送认证邮件
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()
    if form.validate_on_submit():
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm',
                   user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/signup.html', form=form)



@app.route('/confirm/<token>')
@login_required
# 确认用户的账户
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    # 调用 confirm() 方法，根据确认结果显示不同的Flash 消息。
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    # User 模型中 confirmed 属性的值会被修改并添加到会话中，请求处理完后，这两个操作被提交到数据库
    return redirect(url_for('main.index'))
# 重新发送确认邮件
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account','auth/email/confirm',
               user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
# 这个路由为 current_user(即已登录的用户，也是目标用户)重做了一遍注册路由中的操 作。
# 这个路由也用 login_required 保护，确保访问时程序知道请求再次发送邮件的是哪个 用户。

# 更改邮件重新认证
def reset_email():
    form = ResetEmailForm()
    if current_user.confirmed:
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, 'Confirm Your Email', 'auth/email/confirm',
                   user=current_user, token=token)
        flash('A new  email has been sent to you by email.')
        if current_user.confirm(token):
        flash('You have reset your email. Thanks!')
    return redirect(url_for('main.index'))
