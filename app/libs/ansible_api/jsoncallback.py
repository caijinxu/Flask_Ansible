import datetime
import json
from functools import partial
from ansible.plugins.callback import CallbackBase
from ansible.inventory.host import Host
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase
from pymongo import MongoClient
import time
from app.secure import *


def current_time():
    return '%s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


class JsonCallback(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'json'

    def __init__(self, work_uuid, work_name, exec_mode, options, describe, yaml_content='', module_name=None,
                 module_args=None, pattern=None, display=None, username=''):
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
        self.callbackresult = {
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
            self.callbackresult['pattern'] = self.pattern
            self.callbackresult['module_name'] = self.module_name
            self.callbackresult['module_args'] = self.module_args

        if self.exec_mode == 'playbook':
            self.callbackresult['yaml_content'] = self.yaml_content
        self.results = []
        super(JsonCallback, self).__init__(display)

    def _new_play(self, play):
        return {
            'play': {
                'name': play.get_name(),
                'id': str(play._uuid),
                'duration': {
                    'start': current_time()
                }
            },
            'tasks': []
        }

    def _new_task(self, task):
        return {
            'task': {
                'name': task.get_name(),
                'id': str(task._uuid),
                'duration': {
                    'start': current_time()
                }
            },
            'hosts': {}
        }



    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))
        self.callbackresult['detail'] = {'plays': self.results}
        self.mongo.inster(self.callbackresult)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))
        self.callbackresult['detail'] = {'plays': self.results}
        self.mongo.inster(self.callbackresult)

    def v2_playbook_on_handler_task_start(self, task):
        self.results[-1]['tasks'].append(self._new_task(task))
        self.callbackresult['detail'] = {'plays': self.results}
        self.mongo.inster(self.callbackresult)

    def _convert_host_to_name(self, key):
        if isinstance(key, (Host,)):
            return key.get_name()
        return key

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        hosts = sorted(stats.processed.keys())

        summary = {}
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s

        custom_stats = {}
        global_custom_stats = {}
        if stats.custom:
            custom_stats.update(dict((self._convert_host_to_name(k), v) for k, v in stats.custom.items()))
            global_custom_stats.update(custom_stats.pop('_run', {}))

        output = {
            'plays': self.results,
            'stats': summary,
            'custom_stats': custom_stats,
            'global_custom_stats': global_custom_stats,
        }
        self.callbackresult['detail'] = output
        self.mongo.inster(self.callbackresult)
        print(output)

    def _record_task_result(self, on_info, result, **kwargs):
        """This function is used as a partial to add failed/skipped info in a single method"""
        host = result._host
        task = result._task
        print(dir(result._task))
        print(dir(result))
        print(result.is_failed())
        print(result.is_changed())
        print(result.is_skipped())
        print('on_info',on_info)
        task_result = result._result.copy()
        task_result.update(on_info)
        task_result['action'] = task.action
        self.results[-1]['tasks'][-1]['hosts'][host.name] = task_result
        end_time = current_time()
        self.results[-1]['tasks'][-1]['task']['duration']['end'] = end_time
        self.results[-1]['play']['duration']['end'] = end_time
        output = {
            'plays': self.results,
        }
        self.callbackresult['detail'] = output
        self.mongo.inster(self.callbackresult)

    def __getattribute__(self, name):
        print('name',name)
        """Return ``_record_task_result`` partial with a dict containing skipped/failed if necessary"""
        if name not in ('v2_runner_on_ok', 'v2_runner_on_failed', 'v2_runner_on_unreachable', 'v2_runner_on_skipped'):
            return object.__getattribute__(self, name)

        on = name.rsplit('_', 1)[1]
        print('on',on)
        on_info = {
            "status": on
        }
        return partial(self._record_task_result, on_info)
