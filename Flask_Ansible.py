# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/5/16
"""
from app import create_app
from app.models import db

__author__ = 'caijinxu'


app = create_app()

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)