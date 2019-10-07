# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/29
"""
from app.libs.utils.net_tool import NmapDev
from app.secure import password_list, ssh_port_list
import os
__author__ = 'caijinxu'


class Scanip:
    def __init__(self, iplist):
        self.iplist = iplist
        self.liveip = []

    def get_nmapliveip(self):
        for net in self.iplist:
            self.liveip += NmapDev.NmapLiveIP(net)
        return self.liveip

    @staticmethod
    def trylogin(iplist, loginfolist=''):
        """生成尝试登录信息列表，每个ip尝试登录"""
        res = []
        if not loginfolist:
            loginfolist = createlogininfo()
        for ip in iplist:
            print(ip, loginfolist)
            res.append({"ip": ip, 'loginfolist': loginfolist})
        return res

appdir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
keyfilepath = appdir+'/keyfile/'
keyflielist = os.listdir(appdir+'/keyfile/')


def createlogininfo():
    """
    生成登录可能的密码，key，port信息
    :return: [{'port': 22, 'password': 'cnfoldc'}，{'port': 22, 'keyfile': 'F:\\Cai\\Desktop\\python\\devops\\app/keyfile/vm'}]
    """
    result = []
    for port in ssh_port_list:
        for passwd in password_list:
            info = {}
            info['port'] = port
            info['password'] = passwd
            result.append(info)
        for keyfile in keyflielist:
            info = {}
            info['port'] = port
            info['keyfile'] = keyfilepath +keyfile
            result.append(info)
    return result


