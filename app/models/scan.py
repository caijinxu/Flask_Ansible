# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/28
"""
from app.models.base import Base
from sqlalchemy import Column, String, Text, SmallInteger
from app.libs.enums import SshStatus

__author__ = 'caijinxu'


class Scan(Base):
    """自动扫描IP信息表"""
    __tablename__ = "sacnipinfo"
    ip = Column(String(64), primary_key=True, )
    ssh_port = Column(String(32), nullable=True)
    ssh_passwd = Column(String(255), default='')
    ssh_user = Column(String(255), default='')
    ssh_keyfile = Column(String(255), default='')
    _ssh_status = Column('ssh_status', SmallInteger, default=0)
    remarks = Column(String(255), default='', comment='备注')

    @property
    def ssh_status(self):
        return SshStatus(self._ssh_status)

    @ssh_status.setter
    def ssh_status(self, status):
        self._ssh_status = status.value

