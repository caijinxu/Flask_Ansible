# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/1/4
"""

__author__ = 'caijinxu'

class Ansible_Utils:

    @staticmethod
    def make_hostinfo(hostlist, gruopname='dynamic_host'):
        hosts = []
        result = {}
        for host in hostlist:
            hostinfo = {
                "username": host.ssh_user,
                "ip": host.ip,
                # "hostname": host.hostname,
                "port": host.ssh_port
            }
            try:
                hostinfo['hostname'] = host.hostname
            except:
                hostinfo['hostname'] = host.ip
            if host.ssh_passwd and host.ssh_passwd != '':
                hostinfo['password'] = host.ssh_passwd
            if host.ssh_keyfile and host.ssh_keyfile != '':
                hostinfo['ssh_key'] = host.ssh_keyfile

            hosts.append(hostinfo)

        result[gruopname] = {
            "hosts": hosts
        }
        return result
