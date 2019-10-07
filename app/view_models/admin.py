import logging
import json
import traceback
from app.models import db
from app.models.cmdb import ServerInfo, BusinessLine, Scan
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from flask_login import current_user
from sqlalchemy.orm import joinedload
from flask import current_app, flash
from flask_admin.babel import gettext, ngettext, lazy_gettext
from flask_admin.contrib.fileadmin import FileAdmin
import os
from wtforms import SelectField
from app.libs.utils.aes_decryptor import Prpcrypt
from wtforms import fields
from wtforms import validators
from app.forms.base import BaseForm
from jinja2 import Markup


class NewBaseView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None):
        joins = {}
        count_joins = {}

        query = self.get_query().filter_by()
        count_query = self.get_count_query() if not self.simple_list_pager else None

        # Ignore eager-loaded relations (prevent unnecessary joins)
        # TODO: Separate join detection for query and count query?
        if hasattr(query, '_join_entities'):
            for entity in query._join_entities:
                for table in entity.tables:
                    joins[table] = None

        # Apply search criteria
        if self._search_supported and search:
            query, count_query, joins, count_joins = self._apply_search(query,
                                                                        count_query,
                                                                        joins,
                                                                        count_joins,
                                                                        search)

        # Apply filters
        if filters and self._filters:
            query, count_query, joins, count_joins = self._apply_filters(query,
                                                                         count_query,
                                                                         joins,
                                                                         count_joins,
                                                                         filters)

        # Calculate number of rows if necessary
        count = count_query.scalar() if count_query else None

        # Auto join
        for j in self._auto_joins:
            query = query.options(joinedload(j))

        # Sorting
        query, joins = self._apply_sorting(query, joins, sort_column, sort_desc)

        # Pagination
        query = self._apply_pagination(query, page, page_size)

        # Execute if needed
        if execute:
            query = query.all()
        return count, query

    def delete_model(self, model):
        """
            Delete model.

            :param model:
                Model to delete
        """
        try:
            self.on_model_delete(model)
            self.session.flush()
            model.status = 1
            # self.session.delete(model)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
                # log.exception('Failed to delete record.')
            self.session.rollback()
            return False
        else:
            self.after_model_delete(model)
        return True


class ServerInfoModleView(NewBaseView):
    can_create = False
    edit_modal = True
    list_template = 'myadmin/serverinfo_list.html'
    column_labels = {
        "ip": "IP地址",
        "hostremarks": "主机名",
        "vcpus": "vcpus",
        "memory": "内存/MB",
        "system_ver": "系统版本",
        "vendor": "主机厂商",
        "business.name": "所属业务",
        "business": "所属业务",
        "server_status": "资产状态",
        "remark": "备注",
    }
    form_extra_fields = {
        'server_status': SelectField(coerce=int, choices=[(0, 'running'), (1, 'close')])
    }
    column_choices = {
        'server_status': [(0, 'running'), (1, 'close')]
    }
    can_delete = False
    column_editable_list = ['hostremarks']
    column_list = ("ip", 'hostremarks', 'vcpus', 'memory', 'system_ver', 'vendor', 'business.name', 'server_status',
                   "remark")
    form_excluded_columns = ['create_time', 'status', 'ssh_port', 'ssh_user', 'ssh_passwd', 'ssh_keyfile']  # 从列表视图中隐藏列


serverinfoview = ServerInfoModleView(ServerInfo, db.session, name="服务器信息", endpoint='serverinfo', url="/cmdb/serverinfo/")


class BusinessLineModelView(NewBaseView):
    column_labels ={
        'name': "业务名",
        'describe': "详细说明"
    }
    column_list = ("name", "describe")
    form_excluded_columns = ['create_time', 'status', 'businessline']
    column_editable_list = ['name', 'describe']


businessview = BusinessLineModelView(BusinessLine, db.session, name='业务信息', endpoint='business', url="/cmdb/business/")


class ScanModelView(NewBaseView):
    list_template = 'myadmin/autoscan.html'
    form_excluded_columns = ['create_time', 'status']
    column_list = ('ip', 'ssh_status', 'remarks', 'create_time')
    # can_edit = False
    edit_modal = True
    create_modal = True
    column_editable_list = ['remarks']
    column_labels = {
        'ip': "IP地址",
        'ssh_port': "SSH端口",
        'ssh_passwd': "SSH密码",
        'ssh_user': "SSH用户",
        'ssh_keyfile': "SSH KEY",
        'ssh_status': "连接状态",
        'remarks': "备注"
    }


scanview = ScanModelView(Scan, db.session, name="扫描发现主机", endpoint='autoscan', url="/cmdb/autoscan/")


class RoleFileView(FileAdmin):
    editable_extensions = ('md', 'yml', 'py', 'j2')  # 可编辑文件扩展名
    can_delete = False
    can_delete_dirs = False


rolesdir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'playbook/roles')
roleview = RoleFileView(rolesdir, name="RoleFile", endpoint="roles", url='/ansible/roles')


class InstanceView(NewBaseView):

    edit_modal = True
    create_modal = True
    form_excluded_columns = ['status']
    column_labels = {
        'instance_name': "实例名称",
        'type': "实例类型",
        'db_type': "数据库类型",
        'host': "实例连接",
        'port': "端口",
        'user': "用户",
        'password': "密码",
        'service_name': "Oracle service name",
        'sid': "Oracle sid",
        'update_time': "最近更新时间"
    }
    column_list = ('id', 'instance_name', 'type', 'db_type', 'host', 'port', 'user', 'password')
    form_columns = ('instance_name', 'type', 'db_type', 'host', 'port', 'user', 'password', 'service_name', 'sid')
    # form_widget_args = {
    #     "instance_name": {'readonly': True}
    # }
    form_edit_rules = ('type', 'db_type', 'host', 'port', 'user', 'password', 'service_name', 'sid')
    # edit_modal_template = 'myadmin/sql/edit.html'
instanceview = InstanceView(Instance, db.session, name='实例列表', endpoint='instance', url="/sql/instance/")



