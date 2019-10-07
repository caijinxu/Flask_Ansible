# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/1/4
"""
import pymongo
from app.secure import *
__author__ = 'caijinxu'


class Mongo:
    def __init__(self):
        self.host = MONGO_HOST
        self.port = MONGO_PORT
        self.database = MONGO_DATABASE
        self.username = MONGO_USERNAME
        self.password = MONGO_PASSWORD
        self.client = pymongo.MongoClient(
            'mongodb://%s:%s@%s:%s/%s' % (self.username, self.password, self.host, self.port, self.database))

