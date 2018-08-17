import self as self
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db
import hashlib
from flask import request


# 定义 Role 和 User 模型


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(db.Boolean, default=False, index=True)
    permissions = Column(Integer)

    users = relationship('User', backref='role', lazy='dymanic')
    # 向 User 模型中添加一个 role 属性使 roles 和 users 建立关系
    #  users 属性将返回与角色相关联的用户组成的列表


@property
def password(self):
    raise AttributeError('password is not a readable attribute')


@password.setter
def password(self, password):
    self.password_hash = generate_password_hash(password)


def verify_password(self, password):
    return check_password_hash(self.password_hash, password)


def __repr__(self):
    return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
                db.session.commit()


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    # 字段:用户名,邮件,密码,?
    username = Column(String(64), unique=True, index=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(128))
    confirmed = Column(Boolean, default=False)

    # 在某个页面中生成大量头像 计算量大耗cup,把头像直接成好缓存数User 模型里
    # 字段:用户Gravatar头像/MD5散列值URL缓存
    avatar_hash = Column(String(32))
    # 字段:用户真实姓名、所在地、自我介绍、注册日期和最后访问日期。
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    # db.String 和 db.Text 的区别在于后者不需要指定最大长度。
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # default 参数可以接受函数作为默认值

    role_id = Column(Integer, ForeignKey('roles.id'))

    # 添加到 User 模型中的 role_id 列 被定义为外键  通过db.ForeignKey() 把  roles 表中行的 id 值(roles.id) 传给 user 表中的 role_id。

    def __init__(self, email=None, username=None):

        self.username = username

    self.email = email

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 定义默认用户角色
        if self.role is None:
            # 管理员由保存在设置变量 FLASKY_ADMIN 中的电子邮件地址识别
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # 使用缓存的 MD5 散列值生成 Gravatar URL
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    # 检查用户是否有指定权限
    # can() 方法在请求和赋予角色这两种权限之间进行位与操作。
    # 如果角色中包含请求的所有权限位，则返回 True，表示允许用户执行此项操作
    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    # 检查管理员权限is_administrator()
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):

        return '<User %r>' % self.username

    # 生成令牌有效期默认为一小时

    def generate_confirmation_token(self, expiration=3600):

        s = Serializer(current_app.config['SECRET_KEY'], expiration)

    return s.dumps({'confirm': self.id})

    # 检验令牌

    def confirm(self, token):

        s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
        # 检验通过新添加的 confirmed 属性设为 True。
    except:
        return False
    # 检查令牌中的 id 是否和存储在 current_user 中的已登录 用户匹配。
    # 即使恶意用户知道如何生成签名令牌，也无法确认别人的账户
    if data.get('confirm') != self.id:
        return False
    self.confirmed = True
    db.session.add(self)
    return True

    # 修改邮箱
    def change_email(self, token):
        # ...
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    # 从会话中存储的用户 ID( unicode ID 作为参数) 重新加载用户对象 user_loader 回调函数 找不到用户返回 none

    @login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    # 刷新用户最后访问时间 last_seen 每次收到用户的请求时都要调用 ping() 方法
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 选择标准的或加密的 Gravatar URL 基以匹配用户的安全需求
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash =self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        # gravatar() 方法会使用模型中保存的散列值,模型没有就计算
        # 头像URL由URL基、用户电子邮件地址的MD5散列值和参数组成，而且各参数都设定了默认值
        # 若用户更新了电子邮件 地址，则会重新计算散列值
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


# 出于一致性考虑定义AnonymousUser 类
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


# 权限常量  Permission 类为所有位定义了常量以便于获取
class permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLE = 0x04
    MODERATE_COMMENT = 0x08
    ANMINSITER = 0x80

# 文章模型
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    # 字段: 正文/时间戳/作者(id) 1个作者多篇文章
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
     class User(UserMixin, db.Model):
         # ...
posts = db.relationship('Post', backref='author', lazy='dynamic')