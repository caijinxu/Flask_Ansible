# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/1/23
"""
from wtforms import StringField
from wtforms.fields import core
from wtforms.fields import html5
from wtforms.fields import simple
from wtforms import validators
from wtforms import widgets
from app.forms.base import BaseForm, DataRequired
from app.models.user import User
__author__ = 'caijinxu'


class RegisterForm(BaseForm):
    username = StringField(
        label='用户名',
        validators=[
           DataRequired(),
            validators.Length(2, 15, message='昵称至少需要两个字符，最多15个字符')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control'},
        default='root'
    )

    password = simple.PasswordField(
        label='密码',
        validators=[
            validators.DataRequired(message='密码不能为空.')
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control'}
    )

    pwd_confirm = simple.PasswordField(
        label='重复密码',
        validators=[
            validators.DataRequired(message='重复密码不能为空.'),
            validators.EqualTo('password', message="两次密码输入不一致")
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control'}
    )

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise validators.ValidationError('用户名已存在')


class LoginForm(BaseForm):
    username = StringField(
        label='用户名',
        validators=[
            DataRequired(),
            validators.Length(2, 15, message='昵称至少需要两个字符，最多15个字符')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control'},
        default='root'
    )

    password = simple.PasswordField(
        label='密码',
        validators=[
            validators.DataRequired(message='密码不能为空.')
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control'}
    )

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not user:
            raise validators.ValidationError('用户名不存在')
        elif not user.is_active:
            raise validators.ValidationError("用户账户未启用")


class ChangePasswordForm(BaseForm):
    username = StringField(
        label='用户名',
        validators=[
            DataRequired(),
            validators.Length(2, 15, message='昵称至少需要两个字符，最多15个字符')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control'},
        default='root'
    )

    old_password = simple.PasswordField(
        label='原有密码',
        validators=[
            DataRequired()],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control'}
    )
    new_password1 = simple.PasswordField(
        label='新密码',
        validators=[
            DataRequired(),
            validators.Length(6, 10, message='密码长度至少需要在6到20个字符之间'),
            validators.EqualTo('new_password2', message='两次输入的密码不一致')],
        render_kw={'class': 'form-control'}
    )

    new_password2 = simple.PasswordField(
        label='确认新密码',
        validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not user:
            raise validators.ValidationError('用户名不存在')

