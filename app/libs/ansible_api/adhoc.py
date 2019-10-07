# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/19
"""
from app.libs.ansible_api import Base
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible import constants as C
from app.libs.ansible_api.callback import ModelResultsCollector
from app.libs.ansible_api.callback_mongo import ResultCallback
from app.libs.ansible_api.jsoncallback import JsonCallback
__author__ = 'caijinxu'


class Adhoc(Base):

    def run(self, workname, host_list, module_name, module_args, work_uuid, username, callback='mongo', describe=''):

        """
        run module from andible ad-hoc.
        module_name: ansible module_name
        module_args: ansible module args
        """
        play_source = dict(
            name=workname,
            hosts=host_list,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=module_args))]
        )

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        try:
            self.host_list = self.inventory.list_hosts(host_list)
            print("self.host_list", self.host_list)
        except Exception as e:
            self.host_list = []
        if len(self.host_list) == 0:
            # self.logger.error(self.log_prefix + '准备工作失败，原因：没有匹配主机名')
            return False, '执行失败，没有匹配主机名'
        tqm = None
        # if self.redisKey:self.callback = ModelResultsCollectorToSave(self.redisKey,self.logId)
        # else:self.callback = ModelResultsCollector()
        # self.callback = ModelResultsCollector()
        if callback == 'mongo':
            self.callback = JsonCallback(work_uuid, workname, 'adhoc', self.options, describe, module_name=module_name,
                                           module_args=module_args, pattern=host_list, username=username)
        else:
            self.callback = ModelResultsCollector()
        import traceback
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback="minimal",
            )
            tqm._stdout_callback = self.callback
            C.HOST_KEY_CHECKING = False  # 关闭第一次使用ansible连接客户端是输入命令
            tqm.run(play)
            print("tqm.run")
        except Exception as err:
            print(traceback.print_exc())
            # DsRedis.OpsAnsibleModel.lpush(self.redisKey,data=err)
            # if self.logId:AnsibleSaveResult.Model.insert(self.logId, err)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def get_model_result(self):
        self.results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.callback.host_ok.items():
            # hostvisiable = host.replace('.','_')
            self.results_raw['success'][host] = result._result

        for host, result in self.callback.host_failed.items():
            # hostvisiable = host.replace('.','_')
            self.results_raw['failed'][host] = result._result

        for host, result in self.callback.host_unreachable.items():
            # hostvisiable = host.replace('.','_')
            self.results_raw['unreachable'][host]= result._result
        # return json.dumps(self.results_raw)
        return self.results_raw