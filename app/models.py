'''
@Software: PyCharm
@File: model.py
@Author: PySean
@Time: Dec 05, 2020
'''
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin, current_user
from . import db, login_manager
from bson.objectid import ObjectId
from datetime import datetime
import bleach
from markdown import markdown


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


def generate_reset_password_confirmation_token(email, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'password_reset': email})


def generate_change_email_confirmation_token(email, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'change_email': email})


def encrypt_passowrd(password):
    return generate_password_hash(password)


def verify_password(user_password, password):
    return check_password_hash(user_password, password)


class Role(db.Document):
    name = db.StringField()
    permissions = db.IntField()
    default = db.BooleanField()


class User(UserMixin, db.Document):
    email = db.EmailField(max_length=64)
    username = db.StringField(max_length=64, required=True)
    role = db.StringField(max_length=32, default='User')
    password_hash = db.StringField(max_length=128, required=True)
    # confirmed = db.BooleanField(default=False)
    activate = db.BooleanField(default=True)
    followers = db.ListField()
    following = db.ListField()
    member_since = db.DateTimeField(default=datetime.utcnow())
    last_since = db.DateTimeField(default=datetime.utcnow())


@login_manager.user_loader
def load_user(user_id):
    user = User.objects(id=ObjectId(user_id)).first()
    return Temp(id=str(user.id), username=user.username, email=user.email,
                password=user.password_hash, activate=user.activate, role=user.role,
                last_since=user.last_since, member_since=user.member_since)


class Temp(UserMixin):
    is_active = True
    is_anonymous = False
    is_authenticated = True
    email = ''
    username = ''

    def __init__(self, id, username, email, password, activate, role, last_since, member_since):
        self.id = str(id)
        self.username = username
        self.email = email
        self.password_hash = password
        self.activate = activate
        self.last_since = last_since
        self.member_since = member_since
        conn = Role.objects(name=role).first()
        self.role = Role(name=role, permissions=conn.permissions, default=conn.default).save()

    def get_id(self):
        return self.id

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def can(self, permission):
        return self.role is not None and \
               (self.role.permissions & permission) == permission

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return self.username

    def ping(self):
        User.objects(email=self.email).update(last_since=datetime.utcnow())
        # MongoClient().blog.User.update({'temp': self.email}, {'$set': {'last_since': datetime.utcnow()}})

    def is_following(self, user):
        temp = User.objects(username=self.username).get('following')
        for i in range(temp.__len__()):
            if temp[i][0] == user.username:
                return True
        return False


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False

    def is_administrator(self):
        return False


def body_html(body):
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                    'h1', 'h2', 'h3', 'p']
    return bleach.linkify(bleach.clean(markdown(body, output_format='html'),
                                       tags=allowed_tags, strip=True))


login_manager.anonymous_user = AnonymousUser


class Post:
    def __init__(self, body):
        self.body = body
        self.body_html = ''

    def new_article(self):
        self.body_html = body_html(self.body)
        collection = {
            'username': current_user.username,
            'user_id': current_user.id,
            'body': self.body,
            'issuing_time': datetime.utcnow(),
            'body_html': self.body_html,
            'comments': []
        }
        # MongoClient().blog.Aritical.insert(collection)
