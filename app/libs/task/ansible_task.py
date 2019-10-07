from threading import Thread
from app.libs.ansible_api.adhoc import Adhoc
from app.libs.ansible_api.playbook import PLAYBOOK


def ansible_adhoc(resource, workname, host_list, module_name, module_args, work_uuid, username, describe):
    rbt = Adhoc(resource)
    print(rbt.inventory.hosts)
    rbt.run(workname, host_list, module_name, module_args, work_uuid, username, describe=describe)


def run_ansible_adhoc(resource, workname, host_list, module_name, module_args, work_uuid, username, describe):
    thr = Thread(target=ansible_adhoc, args=[resource, workname, host_list, module_name, module_args, work_uuid,
                                             username, describe])
    thr.start()


def ansible_playbook(resource, playbook, workname, work_uuid, username, describe, yaml_content):
    rbt = PLAYBOOK(resource)
    print(rbt.inventory.hosts)
    rbt.run_playbook(playbook, workname, work_uuid, username, describe, yaml_content)


def run_ansible_playbook(resource, playbook, workname, work_uuid, username, describe, yaml_content):
    thr = Thread(target=ansible_playbook, args=[resource, playbook, workname, work_uuid, username, describe,
                                                yaml_content])
    thr.start()


def run_get_facts(resource):
    """获取主机配置信息"""
    hostlist = []
    for v in resource.values():
        for ipinfo in v['hosts']:
            hostlist.append(ipinfo['ip'])
    rbt = Adhoc(resource)
    rbt.run(workname="获取主机配置信息", host_list=hostlist, module_name="setup", module_args='', work_uuid='', username='root',callback='no')
    return rbt.get_model_result()

