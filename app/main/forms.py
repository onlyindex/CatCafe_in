from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, RecaptchaField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import validators, ValidationError
from ..models import User


# flask vs flaskform区别? flaskfrom是 form 的subclass 版本更新后统一使用 flaskform 和 wtform 中的 form 区分开了
#  Any view using FlaskForm to process the request is already getting CSRF protection.
# import fields ( 表单字段 name submit ) from wtforms  import DataRequired()验证函数 from wtforms.validators
# 注册表单类Creating Forms
class SignupForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25 / 64),
                                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                               'Usernames must have only letters',
                                               'numbers, dots or underscores')])
    # 验证函数Regexp() 确保 username 字段只包含字母、数字、下划线和点号。
    email = StringField('Email Address', validators=[DataRequired(), Length(6, 64), Email())
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_pwd', message='Passwords must match')])
    # 验证函数EqualTo()附属在confirm_pwd 。
    confirm_pwd = PasswordField('Repeat Password to Confirm', validators=[DataRequired()])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    submit = SubmitField('Signup')

    # 为email 和 username 字段定义了验证函数，确保邮件和用户名没被占用
    # 验证失败，可以抛出 ValidationError 异常，其参数就是错误消息

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


# 登录表单类
class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')


# 评论表单类
class CommentForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(4, 25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')
    # 名为username type='text' | 名为submit type='submit' 文本字段和提交对象
    # validators 可选参数指定一个由验证函数组成的列表,在接受用户提交的数据之前验证数据
    # 验证函数 DataRequired()确保提交字段不为空 Required() wft3.0失效


# 重置邮箱表单类
class ResetEmailForm(FlaskForm):
    restemail = StringField('New Email Address', [validators.Length(min=6, max=35)])
    submit = SubmitField('Submit')


# 个人资料编辑器
class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


# 管理员使用的资料编辑器(还能编辑用户的电子邮件、用户名、确认状态和角色)
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    # 添加 coerce=int 参数，从而把字段的值转换为整数， 而不使用默认的字符串
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

# 博客表单
class PostForm(Form):
    body = TextAreaField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')
