# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/28
"""

__author__ = 'caijinxu'
from app.models import db
from app.models.cmdb import ServerInfo
from app.libs.utils.net_tool import SshClient
from app.models.cmdb import Scan
from app.libs.enums import SshStatus
from threading import Thread
from flask import current_app


def trylogin(app, ip, loginlist):
    with app.app_context():
        for logininfo in loginlist:
            sshclient = SshClient(ip, port=logininfo.get('port'), passwd=logininfo.get('password'), keyfile=logininfo.get('keyfile'))
            res = sshclient.AutoLogin()
            print(res)
            if res.get('status') == "success":
                scanip = Scan.query.filter(Scan.ip == ip).first()
                with db.auto_commit():
                    if not scanip:
                        scanip = Scan()
                        scanip.ip = ip
                        scanip.ssh_port = logininfo.get('port')
                        scanip.ssh_passwd = logininfo.get('password')
                        scanip.ssh_keyfile = logininfo.get('keyfile')
                        scanip.ssh_user = "root"
                        scanip.ssh_status = SshStatus.success
                        db.session.add(scanip)
                    else:
                        scanip.ssh_port = logininfo.get('port')
                        scanip.ssh_passwd = logininfo.get('password')
                        scanip.ssh_keyfile = logininfo.get('keyfile')
                        scanip.ssh_user = "root"
                        scanip.ssh_status = SshStatus.success
                        scanip.status = 1
                break


def run_trylogin(ip, loginlist):
    app = current_app._get_current_object()
    thr = Thread(target=trylogin, args=[app, ip, loginlist])
    thr.start()
    return thr

