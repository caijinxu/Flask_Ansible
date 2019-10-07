# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/1/23
"""
from flask import render_template, redirect, current_app, g
from flask import request, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from . import web
from app.forms.auth import RegisterForm, LoginForm, ChangePasswordForm
from app.models.user import User
from app.models import db

__author__ = 'caijinxu'


@web.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request)
    if request.method == 'POST' and form.validate():
        user = User()
        user.set_attrs(form.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, False)
        return redirect(url_for('web.login'))
    return render_template('auth/register.html', form=form)


@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next or not next.startswith('/'):
                next = url_for('web.autoscan')
            return redirect(next)
        else:
            flash('账号不存在或密码错误', category='login_error')
    return render_template('auth/login.html', form=form)


@web.route('/change/password', methods=['GET', 'POST'])
@login_required
def change_password():
    # 只能由root用户修改密码
    form = ChangePasswordForm(request)
    if request.method == 'POST' and form.validate() and current_user.username == 'root':
        with db.auto_commit():
            user = User.query.filter_by(username=form.username.data).first()
            user.password = form.new_password1.data
        flash('密码已更新成功,请联系管理员重新激活账户')
        return redirect(url_for('web.login'))
    return render_template('auth/change_password.html', form=form)


@web.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.login'))
