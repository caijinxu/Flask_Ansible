# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/28
"""
import nmap
import paramiko
__author__ = 'caijinxu'


class NmapDev:
    """nmap  扫描ip是否存活"""

    @staticmethod
    def NmapLiveIP(Net):
        """
        扫描网段或者IP中存活主机IP
        :param Net: 192.168.15.202 或 192.168.15.0/24
        :return: 存活ip列表
        """
        nm = nmap.PortScanner()
        nm.scan(hosts=Net, arguments=' -n -sP -PE')
        hostlist = nm.all_hosts()
        return hostlist


class SshClient:

    def __init__(self, ip, passwd='', keyfile='', port=22, user='root'):
        self.ip = ip
        self.passwd = passwd
        self.keyfile = keyfile
        self.port = port
        self.user = user
        self.result = {}

    def AutoLogin(self):
        """
        根据是否有密码自动选择相应方式尝试登录
        """
        if self.passwd != '':
            return self.PasswdLogin()
        else:
            return self.Rsakeylogin()

    def PasswdLogin(self, cmdlist=None):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, self.port, self.user, self.passwd)
            self.result['status'] = 'success'
            if cmdlist:
                for cmd in cmdlist:
                    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
                    self.result[cmd] = stdout.read()
            ssh.close()
        except Exception as e:
            print(e)
            # TODO : log
            self.result["status"] = "failed"
            self.result['res'] = e
        return self.result

    def Rsakeylogin(self, cmdlist=None):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            key = paramiko.RSAKey.from_private_key_file(self.keyfile)
            ssh.connect(self.ip, self.port, self.user, pkey=key, timeout=2)
            self.result["status"] = "success"
            if cmdlist:
                for cmd in cmdlist:
                    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
                    self.result[cmd] = stdout.read()
            ssh.close()
        except Exception as e:
            print(e)
            # TODO : log
            self.result["status"] = "failed"
            self.result['res'] = e
        return self.result