# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/5/16
"""

__author__ = 'caijinxu'


SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:123456@127.0.0.1/devops'
SECRET_KEY = '\x9c.*E\xa7z\xe8\xa0\xf1'  # 使用前请重新生成


password_list = ['123456', ]  # 常用密码，不建议配置
ssh_port_list = [22]

MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017
MONGO_DATABASE = "devops"
MONGO_USERNAME = "devopser"
MONGO_PASSWORD = "123456"
MONGO_ANSIBLE_COLLECTION = 'ansible'

