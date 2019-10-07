# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/19
"""
import uuid
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.inventory.host import Host, Group
from ansible.parsing.dataloader import DataLoader
from collections import namedtuple
from app.settings import option_dict
__author__ = 'caijinxu'


class MyInventory:
    """
    生成动态inventory
    """
    def __init__(self, resource, loader, variable_manager):
        self.resource = resource
        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.dynamic_inventory()

    def add_dynamic_group(self, hosts, groupname, groupvars=None):
        """
            add hosts to a group
        """
        self.inventory.add_group(groupname)
        my_group = Group(name=groupname)
        # if group variables exists, add them to group
        if groupvars:
            for key, value in groupvars.items():
                my_group.set_variable(key, value)

        # add hosts to group
        for host in hosts:
            # set connection variables
            hostip = host.get('ip')
            hostname = host.get("hostname", hostip)
            hostport = host.get("port")
            username = host.get("username")
            password = host.get("password")
            ssh_key = host.get("ssh_key")
            my_host = Host(name=hostname, port=hostport)
            self.variable_manager.set_host_variable(host=my_host, varname='ansible_ssh_host', value=hostip)
            self.variable_manager.set_host_variable(host=my_host, varname='ansible_ssh_pass', value=password)
            self.variable_manager.set_host_variable(host=my_host, varname='ansible_ssh_port', value=hostport)
            self.variable_manager.set_host_variable(host=my_host, varname='ansible_ssh_user', value=username)
            self.variable_manager.set_host_variable(host=my_host, varname='ansible_ssh_private_key_file', value=ssh_key)
            self.variable_manager.extra_vars = my_group.get_vars()
            # set other variables
            for key, value in host.items():
                if key not in ["hostname", "port", "username", "password"]:
                    self.variable_manager.set_host_variable(host=my_host, varname=key, value=value)
            # add to group

            self.inventory.add_host(host=hostname, group=groupname, port=hostport)

    def dynamic_inventory(self):
        """
            add hosts to inventory.
        """
        if isinstance(self.resource, list):
            self.add_dynamic_group(self.resource, 'default_group')
        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.items():
                self.add_dynamic_group(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("vars"))


class Base:

    def __init__(self, resource, *args, **kwargs):
        self.resource = resource
        self.inventory = None
        self.variable_manager = None
        self.loader = None
        self.options = None
        self.passwords = None
        self.callback = None
        self.__initializeData()
        self.results_raw = {}
        # self.work_uuid = str(uuid.uuid4())

    def __initializeData(self):
        """ 初始化ansible """
        self._get_options()
        self.loader = DataLoader()
        self.passwords = dict(sshpass=None, becomepass=None)
        myinvent = MyInventory(self.resource, self.loader, self.variable_manager)
        self.inventory = myinvent.inventory
        # print('i', self.inventory)
        self.variable_manager = myinvent.variable_manager

    def _get_options(self):
        keys_list = []
        values_list = []
        for key, value in option_dict.items():
            keys_list.append(key)
            values_list.append(value['default'])
        Options = namedtuple('Options', keys_list)
        self.options = Options._make(values_list)