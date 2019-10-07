# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/5/16
"""
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import Column, Integer, SmallInteger, DATETIME
from flask import current_app
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
__author__ = 'caijinxu'


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self, throw=True):
        try:
            yield
            print(dir(self))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            current_app.logger.exception('%r' % e)
            if throw:
                raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 0
        return super(Query, self).filter_by(**kwargs)


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    __abstract__ = True
    create_time = Column('createtime', DATETIME)
    status = Column(SmallInteger, default=0)
    # __mapper_args__ = {"order_by": create_time.desc()}

    def __init__(self):
        self.create_time = datetime.now()

    @property
    def create_datetime(self):
        if self.create_time:
            return self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    def delete(self):
        self.status = 1

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

