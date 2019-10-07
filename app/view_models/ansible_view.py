import uuid
from flask_login import current_user
from math import ceil
from flask import flash
from app.models import db
from app.models.cmdb import ServerInfo, Scan
from app.libs.task.ansible_task import run_ansible_adhoc, run_get_facts, run_ansible_playbook
import os
import json


def make_hostinfo(hostlist, gruopname='dynamic_host'):
    hosts = []
    result = {}
    for host in hostlist:
        try:
            host.hostname
        except:
            host.hostname = host.ip
        hostinfo = {
            "username": host.ssh_user,
            "ip": host.ip,
            "hostname": host.ip,
            "port": host.ssh_port
        }
        if host.ssh_passwd:
            hostinfo['password'] = host.ssh_passwd
        if host.ssh_keyfile:
            hostinfo['ssh_key'] = host.ssh_keyfile
        hosts.append(hostinfo)
    result[gruopname] = {
        "hosts": hosts
    }
    return result


def run_adhoc(form, iplist):
    """
        生成输入host的登录信息，后台执行adhoc任务
        :return: 任务work_uuid
        """
    work_uuid = str(uuid.uuid4())
    # iplist = form.ip.data
    # if not isinstance(iplist, list):
    #     iplist = iplist.split(';')
    # print(iplist)
    workipinfo = ServerInfo.query.filter(ServerInfo.ip.in_(iplist), ServerInfo.status == 0).all()
    if not workipinfo:
        flash("没有相应的IP信息执行任务")
        return False
    resource = make_hostinfo(workipinfo)
    print(resource)
    try:
        run_ansible_adhoc(resource, form.workname.data, iplist, form.module_name.data, form.module_args.data, work_uuid,
                          current_user.username, form.describe.data)
        return work_uuid
    except:
        return False


def scanaddcmdb(hostip):
    """从scan表加入cmdb，并获取详细配置信息"""
    ipinfo = Scan.query.filter_by(ip=hostip).all()
    if not ipinfo:
        flash("没有相应的IP信息执行任务")
        return False
    server = ServerInfo.query.filter_by(ip=hostip).all()
    if not server:
        resource = make_hostinfo(ipinfo)
        result = get_servers_info(resource)
        if result:
            for fast in result:
                with db.auto_commit():
                    ser = ServerInfo()
                    ser.set_attrs(fast)
                    db.session.add(ser)
                    Scan.query.filter_by(ip=ser.ip).delete()
                    flash(ser.ip + ": 加入CMDB成功")
        else:
            flash(hostip + ":获取主机信息出错，加入CMDB出错")
    else:
        flash('地址已经在cmdb信息中')


def get_servers_info(resource):
    print(type(resource), resource)
    facts = run_get_facts(resource)
    result = []
    print(facts)
    if facts['success']:
        for host, factinfo in facts['success'].items():
            info = factinfo['ansible_facts']
            res = {
                "ip": host
            }
            try:
                res["hostname"] = info["ansible_hostname"]
            except Exception as e:
                print(e)
                res["hostname"] = ''
            try:
                res['vcpus'] = info['ansible_processor_vcpus']
            except Exception as e:
                print(e)
                res['vcpus'] = ''

            try:
                res['memory'] = info['ansible_memory_mb']['real']['total']
            except Exception as e:
                print(e)
                res['memory'] = ''
            try:
                res['mac'] = info['ansible_default_ipv4']['macaddress']
            except Exception as e:
                print(e)
                res['mac'] = ''
            try:
                res['vendor'] = info['ansible_system_vendor']
            except Exception as e:
                print(e)
                res['vendor'] = ''
            try:
                res['serial'] = info['ansible_product_serial']
            except Exception as e:
                print(e)
                res['serial'] = ''
            try:
                res['system_ver'] = info['ansible_distribution'] + ' ' + info['ansible_distribution_version'] + ' ' + \
                                    info['ansible_distribution_release']
            except Exception as e:
                print(e)
                res['system_ver'] = ''

            print(type(resource), resource)
            for v in resource.values():
                for loginfo in v['hosts']:
                    if loginfo['ip'] == host:
                        res['ssh_user'] = loginfo['username']
                        res['ssh_keyfile'] = loginfo.get('ssh_key')
                        res['ssh_passwd'] = loginfo.get('password')
                        res['ssh_port'] = loginfo['port']
            result.append(res)
    return result


def refresh_server(server):
    """通过serverinfo信息获取新的facts"""
    resource = make_hostinfo(server)
    print(resource)
    result = get_servers_info(resource)
    return result


# 生成的ansible动态Inventory信息
"""
resource = {
        "dynamic_host": {
            "hosts": [
                {'username': u'root', 'ssh_key': '/usr/local/scripts/devops/app/keyfile/vm', 'ip': '47.107.186.9',
                 'hostname': 'iZwz9d10hr1juimr3dpjz7Z', 'port': '22'},
            ],
            "vars": {
                "var1": "ansible",

            }
        }
    }
"""


def run_playbook(gourpinfo, form, playbook_content):
    """
    执行playbook
    :param gourpinfo: 以dict传入的执行组名和执行IP地址列表
    :param form: 传入的form信息
    :return: 任务执行的uuid
    """
    # 生成任务执行需要动态登录信息
    inv = {}
    for gourpname, iplist in gourpinfo.items():
        workipinfo = ServerInfo.query.filter(ServerInfo.ip.in_(iplist), ServerInfo.status == 0).all()
        if not workipinfo:
            flash(gourpname + ":没有相应的IP信息执行任务")
            return False
        resource = make_hostinfo(workipinfo, gruopname=gourpname)
        inv.update(resource)
    print(inv)
    # 将yaml内容保存到playbook目录下，文件名为任务uuid
    appdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    work_uuid = str(uuid.uuid4())
    yamlfilename = work_uuid + ".yaml"
    playbook = os.path.join(appdir, 'playbook', yamlfilename)
    print(playbook)
    with open(playbook, 'w') as f:
        f.write(playbook_content)
    run_ansible_playbook(inv, playbook, form.workname.data, work_uuid, current_user.username, form.describe.data,
                         playbook_content)
    return work_uuid


def get_pagination(counts, pagelimit, page):
    """传入总数、分页大小、当前页，返回分页信息"""
    pages = ceil(counts / pagelimit)
    pageination = {}
    if pages > 1:
        pageination['page'] = page
        # 分页大于1，处理分页
        if page - 1 >= 1:
            pageination['previous'] = page - 1
        if page + 1 <= pages:
            pageination['next'] = page + 1
        pageination['pagelist'] = []
        for i in range(-2, 3):
            if 0 < page + i <= pages:
                pageination['pagelist'].append(page + i)
    return pageination


def format_output(taskinfo):
    """整理输出"""
    output = ''
    if taskinfo['mode'] == 'adhoc':
        for play in taskinfo['detail']['plays']:
            for task in play['tasks']:
                for host, reslut in task['hosts'].items():
                    output += host + "| " + reslut['status'] + " ==> \n"
                    try:
                        if reslut['status'] == 'ok':
                            output += reslut['stdout'] + '\n\n'
                        else:
                            output += reslut['stderr'] + "\n\n"
                    except Exception as e:
                        output += json.dumps(reslut, sort_keys=True, indent=4, separators=(',', ': '))
        print(output)
        taskinfo['show'] = output
    else:
        for play in taskinfo['detail']['plays']:
            output += 'PLAY:' + play['play']['name'] + "\n\n"
            for task in play['tasks']:
                if task:
                    output += "TASK:" + task['task']['name'] + "\n"
                    for host, reslut in task['hosts'].items():
                        output += reslut['status'] + '：' + host + '\n'
                output += '\n'
        output += "PLAY RECAP \n"
        try:
            for hostip, stats in taskinfo['detail']["stats"].items():
                output += hostip + " : ok=" + str(stats['ok']) + "  changed=" + str(stats['changed']) \
                          + "  failures=" + str(stats['failures']) + "  unreachable=" + str(stats['unreachable']) \
                          + "  skipped=" + str(stats['skipped']) + "\n"
        except:
            pass
        taskinfo['show'] = output
    taskinfo['detail'] = json.dumps(taskinfo['detail'], sort_keys=True, indent=4, separators=(',', ': '))
    return taskinfo

