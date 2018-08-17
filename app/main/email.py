from sqlalchemy.sql.functions import user
from app import db
from app.main import app
from app.main.forms import SignupForm, ResetEmailForm
from ..email import send_email
from flask import redirect, url_for, render_template, flash
from flask.ext.login import current_user


# 发送确认邮件_注册时候
@auth.route('/register', methods=['GET', 'POST'])
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



@auth.route('/confirm/<token>')
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

# 更改邮件重新确认
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



