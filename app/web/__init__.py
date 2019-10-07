# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/5/16
"""
from flask import Blueprint
__author__ = 'caijinxu'

web = Blueprint('web', __name__, template_folder='templates')

from app.web import auth
from app.web import ansible
from app.web import cmdb
