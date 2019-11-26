from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

from apps import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    # 添加一个default字段，指明一般用户默认的角色
    default = db.Column(db.Boolean, default=False, index=True)
    # permissions字段用来记录不同角色的权限值
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def __str__(self):
        return self.name

    # 添加权限
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    # 移除权限
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    # 重置权限
    def reset_permissions(self):
        self.permissions = 0

    # 检查当前实例是否具备某种权限
    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)

    nickname = db.Column(db.String(16))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    avatar_url = db.Column(db.String(128))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def __str__(self):
        return self.name

    def get_last_seen(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    # 禁止读取密码
    @property
    def password(self):
        raise AttributeError('password 不是一个可读属性')

    # 设置密码
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码，密码正确则返回True
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 用来判断一个用户是否具备某种权限
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    # 用来判断某个用户是否有管理员权限
    def is_administrator(self):
        return self.can(Permission.ADMIN)


# 创建一个匿名用户类，从而实现相应的权限 flask-login
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# 指定项目使用的匿名用户类
login_manager.anonymous_user = AnonymousUser
