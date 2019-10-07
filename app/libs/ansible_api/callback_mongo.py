# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/20
"""
from ansible.plugins.callback import CallbackBase
from pymongo import MongoClient
import time
from app.secure import *
import uuid
__author__ = 'caijinxu'


class ResultModel(object):

    def __init__(self):
        self.host = MONGO_HOST
        self.port = MONGO_PORT
        self.database = MONGO_DATABASE
        self.username = MONGO_USERNAME
        self.password = MONGO_PASSWORD
        self.collection = MONGO_ANSIBLE_COLLECTION
        self.client = MongoClient(
            'mongodb://%s:%s@%s:%s/%s' % (self.username, self.password, self.host, self.port, self.database))
        self.db = self.client[self.database]

    def inster(self, data):
        self.db[self.collection].update({'uuid': data['uuid']}, data, upsert=True)



class ResultCallback(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'storage'

    def __init__(self, work_uuid, work_name, exec_mode, options, describe, yaml_content='', module_name=None, module_args=None, pattern=None, display=None, username=''):
        self.mongo = ResultModel()
        self.work_uuid = work_uuid
        self.work_name = work_name
        self.exec_mode = exec_mode
        self.yaml_content = yaml_content
        self.pattern = pattern
        self.module_name = module_name
        self.module_args = module_args
        self.options = options
        self.describe = describe
        self.result = {
            '_id': self.work_uuid,
            'mode': self.exec_mode,
            'name': self.work_name,
            'uuid': self.work_uuid,
            'describe': self.describe,
            'create_date': time.strftime("%Y-%m-%d", time.localtime()),
            'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'options': self.options,
            'create_ts': round(time.time(), 3),
            'username': username
        }
        if self.exec_mode == 'adhoc':
            self.result['pattern'] = self.pattern
            self.result['module_name'] = self.module_name
            self.result['module_args'] = self.module_args

        if self.exec_mode == 'playbook':
            self.result['yaml_content'] = self.yaml_content

        super(ResultCallback, self).__init__(display)

    def v2_playbook_on_play_start(self, play):
        if not self.result.get('play'):
            self.result['play'] = []
        self.result['play'].append({
            'name': play.name,
            'id': str(play._uuid),
        })

        self.mongo.inster(self.result)

    def v2_playbook_on_task_start(self, task, is_conditional):
        if self.exec_mode == 'adhoc':
            # taskname = self.work_name
            taskname = str(task)
        elif self.exec_mode == 'playbook':
            taskname = task.name

        args_dict = task.args
        print("task", dir(task))
        self.result['task'] = {
            'name': taskname,
            'module': task.action,
            'args': args_dict,
            # 请看ansible/lib/ansible/plugins/strategy/linear.py
            'id': str(task._uuid),
            'start_ts': round(time.time(), 3),
        }
        self.result['task_id'] = str(task._uuid)
        self.result['detail'] = {}
        print('playbook on task start', self.result)
        # self.log_router.write(self.result, self.oper, log_dict=self.log_dict)
        self.mongo.inster(self.result)

    def v2_runner_on_ok(self, result, **kwargs):
        print("ok")
        print('ok ', result._result)
        print('result', dir(result))
        host = result._host
        hstnm = host.get_name()
        self.result['detail'][hstnm] = result._result
        self.result['detail'][hstnm]['start_ts'] = self.result['task']['start_ts']
        self.result['detail'][hstnm]['end_ts'] = round(time.time(), 3)
        self.result['finish_ts'] = round(time.time(), 3)
        # self.log_router.write(self.result, self.oper, log_dict=self.log_dict)
        print(self.result)
        self.mongo.inster(self.result)

    def v2_playbook_on_no_hosts_matched(self):
        print('v2_playbook_on_no_hosts_matched')
        self.result['finish_ts'] = round(time.time(), 3)
        self.result['stats'] = '没有匹配的主机'
        # self.log_router.write(self.result, self.oper, log_dict=self.log_dict)
        self.mongo.inster(self.result)

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())

        summary = {}
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s

        self.result['summary'] = summary
        self.result['finish_ts'] = round(time.time(), 3)
        # self.log_router.write(self.result, self.oper, log_dict=self.log_dict)
        self.mongo.inster(self.result)

    v2_runner_on_failed = v2_runner_on_ok
    v2_runner_on_unreachable = v2_runner_on_ok
    v2_runner_on_skipped = v2_runner_on_ok
    v2_playbook_on_ok = v2_runner_on_ok

