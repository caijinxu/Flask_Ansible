# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/29
"""
from app.models.base import Base, db
from sqlalchemy import Column, String, Text, SmallInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.libs.enums import SshStatus
from app.libs.utils.aes_decryptor import Prpcrypt

__author__ = 'caijinxu'


class Scan(Base):
    """自动扫描IP信息表"""
    __tablename__ = "sacnipinfo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String(64), nullable=False, unique=True)
    ssh_port = Column(String(32), nullable=True)
    _ssh_passwd = Column('ssh_passwd', Text, default='')
    ssh_user = Column(String(255), default='')
    ssh_keyfile = Column(String(255), default='')
    _ssh_status = Column('ssh_status', SmallInteger, default=0)
    remarks = Column(String(255), default='备注', comment='备注')

    @property
    def ssh_passwd(self):
        if self._ssh_passwd:
            return Prpcrypt().decrypt(self._ssh_passwd)

    @ssh_passwd.setter
    def ssh_passwd(self, raw):
        if raw:
            self._ssh_passwd = Prpcrypt().encrypt(raw)

    @property
    def ssh_status(self):
        return SshStatus(self._ssh_status)

    @ssh_status.setter
    def ssh_status(self, status):
        self._ssh_status = status.value


class BusinessLine(Base):
    __tablename__ = "businessline"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    describe = Column(String(255), default='')

    def __repr__(self):
        return self.name


class ServerInfo(Base):
    __tablename__ = "serverinfo"
    ip = Column(String(64), primary_key=True)
    ssh_port = Column(String(32), nullable=True)
    _ssh_passwd = Column('ssh_passwd', Text, default='')
    ssh_user = Column(String(255), default='')
    ssh_keyfile = Column(String(255), default='')
    hostname = Column(String(50), default='', comment='主机hostname')
    hostremarks = Column(String(255), default='', comment='hostname备注')
    vcpus = Column(SmallInteger, comment='主机CPU个数')
    memory = Column(Integer, comment="内存，单位mb")
    system_ver = Column(String(50), default='', comment='系统版本')
    mac = Column(String(512), default='', comment='网卡mac地址')
    vendor = Column(String(255), comment='厂商')
    serial = Column(String(512), comment="序列号")
    server_status = Column(SmallInteger, default=0, comment="0：运行中，1：已下线")
    remark = Column(Text, comment='备注')
    businenss_id = Column(Integer, ForeignKey("businessline.id"))
    business = relationship("BusinessLine", backref="businessline")

    @property
    def ssh_passwd(self):
        if self._ssh_passwd:
            return Prpcrypt().decrypt(self._ssh_passwd)

    @ssh_passwd.setter
    def ssh_passwd(self, raw):
        if raw:
            self._ssh_passwd = Prpcrypt().encrypt(raw)


