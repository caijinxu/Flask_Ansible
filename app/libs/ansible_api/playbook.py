# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/19
"""
from app.libs.ansible_api import Base
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible import constants as C
from ansible.utils.ssh_functions import check_for_controlpersist
from ansible.playbook import Playbook
from ansible.template import Templar
from ansible.utils.helpers import pct_to_int
from app.libs.ansible_api.callback import PlayBookResultsCollector
from app.libs.ansible_api.callback_mongo import ResultCallback
from app.libs.ansible_api.jsoncallback import JsonCallback
__author__ = 'caijinxu'


class PLAYBOOK(Base):

    def run(self, playbook):

        pass

    def run_playbook(self, playbook, workname, work_uuid, username, describe, yaml_content, is_checksyntax=False):
        """

        :param playbooks: playbook路径的列表
        :return:
        """
        if is_checksyntax:
            self._tqm = None
        else:
            # self.callback = PlayBookResultsCollector()
            # self.callback = ResultCallback(work_uuid, workname, 'playbook', self.options, describe,
            #                                yaml_content=yaml_content, username=username)
            self.callback = JsonCallback(work_uuid, workname, 'playbook', self.options, describe,
                                         yaml_content=yaml_content, username=username)
            self._tqm = TaskQueueManager(inventory=self.inventory,
                                         variable_manager=self.variable_manager,
                                         loader=self.loader,
                                         options=self.options,
                                         passwords=self.passwords,
                                         stdout_callback=self.callback)

        check_for_controlpersist(C.ANSIBLE_SSH_EXECUTABLE)

        try:
            pb = Playbook.load(playbook, variable_manager=self.variable_manager, loader=self.loader)
            if self._tqm is not None:
                self._tqm.load_callbacks()
                self._tqm.send_callback('v2_playbook_on_start', pb)

            plays = pb.get_plays()
            for play in plays:
                if play._included_path is not None:
                    self.loader.set_basedir(play._included_path)
                else:
                    self.loader.set_basedir(pb._basedir)
                self.inventory.remove_restriction()

                # Allow variables to be used in vars_prompt fields.
                all_vars = self.variable_manager.get_vars(play=play)
                templar = Templar(loader=self.loader, variables=all_vars)
                play.post_validate(templar)

                if is_checksyntax or self._tqm is None:
                    return True

                batches = self._get_serialized_batches(play)
                if len(batches) == 0:
                    self._tqm.send_callback('v2_playbook_on_play_start', play)
                    self._tqm.send_callback('v2_playbook_on_no_hosts_matched')
                    continue
                for batch in batches:
                    self.inventory.restrict_to_hosts(batch)
                    try:
                        self._tqm.run(play)
                    except Exception as e:
                        print(e)

            self._tqm.send_callback('v2_playbook_on_stats', self._tqm._stats)
            self._tqm.cleanup()
            self.loader.cleanup_all_tmp_files()
            return True
        except Exception as e:
            print(e)
            return False

    def _get_serialized_batches(self, play):
        '''
        Returns a list of hosts, subdivided into batches based on
        the serial size specified in the play.
        '''

        # make sure we have a unique list of hosts
        all_hosts = self.inventory.get_hosts(play.hosts)
        all_hosts_len = len(all_hosts)

        # the serial value can be listed as a scalar or a list of
        # scalars, so we make sure it's a list here
        serial_batch_list = play.serial
        if len(serial_batch_list) == 0:
            serial_batch_list = [-1]

        cur_item = 0
        serialized_batches = []

        while len(all_hosts) > 0:
            # get the serial value from current item in the list
            serial = pct_to_int(serial_batch_list[cur_item], all_hosts_len)

            # if the serial count was not specified or is invalid, default to
            # a list of all hosts, otherwise grab a chunk of the hosts equal
            # to the current serial item size
            if serial <= 0:
                serialized_batches.append(all_hosts)
                break
            else:
                play_hosts = []
                for x in range(serial):
                    if len(all_hosts) > 0:
                        play_hosts.append(all_hosts.pop(0))

                serialized_batches.append(play_hosts)

            # increment the current batch list item number, and if we've hit
            # the end keep using the last element until we've consumed all of
            # the hosts in the inventory
            cur_item += 1
            if cur_item > len(serial_batch_list) - 1:
                cur_item = len(serial_batch_list) - 1

        return serialized_batches
    #
    # def get_playbook_result(self):
    #     self.results_raw = {'skipped': {}, 'failed': {}, 'ok': {}, "status": {}, 'unreachable': {}, "changed": {}}
    #     for host, result in self.callback.task_ok.items():
    #         self.results_raw['ok'][host] = result
    #
    #     for host, result in self.callback.task_failed.items():
    #         self.results_raw['failed'][host] = result
    #
    #     for host, result in self.callback.task_status.items():
    #         self.results_raw['status'][host] = result
    #
    #     # for host, result in self.callback.task_changed.items():
    #     #     self.results_raw['changed'][host] = result
    #
    #     for host, result in self.callback.task_skipped.items():
    #         self.results_raw['skipped'][host] = result
    #
    #     for host, result in self.callback.task_unreachable.items():
    #         self.results_raw['unreachable'][host] = result
    #     return self.results_raw