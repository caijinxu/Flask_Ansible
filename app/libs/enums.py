# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/28
"""
from enum import Enum

__author__ = 'caijinxu'


class SshStatus(Enum):
    """SSH登录状态"""
    success = 1
    false = 0


class MachineType(Enum):
    """设备类型"""
    machine = 0
    kvm = 1
    docker = 2
    xvn = 3
    network = 4
    other = 5


class TaskStatus(Enum):
    """SSH登录状态"""
    running = 0
    success = 1
    false = 2


class TaskMode(Enum):
    """ansible任务类型"""
    adhoc = 0
    playbook = 1


class UserStatus(Enum):
    """用户账户状态"""
    enable = 1
    disable = 0


class ServerStatus(Enum):
    """服务器状态"""
    running = 0
    close = 1

