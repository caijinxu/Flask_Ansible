# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/1/23
"""
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import Column, ForeignKey, func
from sqlalchemy import String, Unicode, DateTime, Boolean
from sqlalchemy import SmallInteger, Integer, Float
from sqlalchemy.orm import relationship
from app.models.base import db, Base
from app import login_manager
__author__ = 'caijinxu'


class User(UserMixin, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(24), nullable=False)
    _password = Column('password', String(100))
    active = Column('active', Boolean, default=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    def generate_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return self.active


@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

