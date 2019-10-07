# -*- coding: utf-8 -*-
"""
create by caijinxu on 2019/1/14
"""
from app.forms.base import BaseForm, DataRequired
from wtforms import StringField
from wtforms.fields import simple
from wtforms.fields import core
from wtforms import widgets
from wtforms.validators import Length, ValidationError
from app.models.cmdb import ServerInfo
import yaml
import traceback
__author__ = 'caijinxu'


class AdhocForm(BaseForm):
    workname = StringField(
        label='任务名',
        validators=[DataRequired(message="任务名不能为空")],
        render_kw={'class': 'form-control', "row": 1, "placeholder": "请输入任务名"},
    )
    ip = core.SelectField(
        label='执行任务ip地址',
        validators=[DataRequired(message="执行任务ip地址不能为空")],
        render_kw={'class': 'form-control selectpicker', 'multiple': "multiple"},
    )
    module_name = StringField(
        label='执行模块名',
        validators=[DataRequired(message="执行模块不能为空")],
        render_kw={'class': 'form-control', "row": 1,  "placeholder": "请输入执行模块名"}
    )
    module_args = StringField(
        label='执行参数',
        render_kw={'class': 'form-control', "row": 1, "placeholder": "请输入执行参数", "required": False}
    )

    describe = StringField(
        label='任务说明',
        render_kw={'class': 'form-control', "row": 1, "required": False}
    )

    def __init__(self, *args, **kwargs):
        super(AdhocForm, self).__init__(*args, **kwargs)
        serverinfo = ServerInfo.query.filter_by().all()
        server_choies = []
        for sinfo in serverinfo:
            if sinfo.hostremarks:
                server_choies.append((sinfo.ip, sinfo.ip + "(" + str(sinfo.hostremarks) + ")"))
            else:
                server_choies.append((sinfo.ip, sinfo.ip))
        self.ip.choices = server_choies


class TaskInfoForm(BaseForm):
    taskuuid = simple.StringField(
        validators=[DataRequired()],
    )


class PlayBookNameForm(BaseForm):
    name = StringField(
        label='playbook名',
        validators=[DataRequired(message="playbook名不能为空"),
                    Length(2, 30, message='名称至少需要两个字符，最多15个字符')],
        render_kw={"placeholder": "输入playbook名", 'class': 'form-control'}
    )


class ReadonlyPlayBookNameForm(BaseForm):
    name = StringField(
        label='playbook名',
        validators=[DataRequired(message="playbook名不能为空"),
                    Length(2, 30, message='名称至少需要两个字符，最多15个字符')],
        render_kw={"placeholder": "输入playbook名", 'class': 'form-control', 'readonly': 'readonly'}
    )


class PlayBookForm(BaseForm):

    remark = StringField(
        label='playbook说明',
        validators=[DataRequired(message="playbook说明不能为空")],
        render_kw={"placeholder": "请填写playbook说明", 'class': 'form-control'}
    )
    content = simple.StringField(
        label='playbook内容',
        validators=[DataRequired(message="playbook内容不能为空")],
        widget=widgets.TextArea(),
        render_kw={"placeholder": "yaml内容,可以直接使用已有的role",  "rows": 10, 'class': 'form-control'}
    )

    def validate_content(self, filed):
        try:
            a = yaml.load(filed.data, yaml.FullLoader)
            print(a)
        except Exception:
            errmsg = "yaml格式错误" + traceback.format_exc(limit=0)
            raise ValidationError(message=errmsg)


class CreatePlayBookForm(PlayBookNameForm, PlayBookForm):
    pass


class EditPlayBookForm(ReadonlyPlayBookNameForm, PlayBookForm):
    pass


class DynamicGroupForm(ReadonlyPlayBookNameForm):
    workname = StringField(
        label='任务名',
        validators=[DataRequired(message="任务名不能为空")],
        render_kw={'class': 'form-control', "row": 1, "placeholder": "请输入任务名"},
    )

    describe = StringField(
        label='任务说明',
        render_kw={'class': 'form-control', "row": 1, "required": False}
    )


def get_selectfield(fieldname):
    serverinfo = ServerInfo.query.filter_by().all()
    server_choies = []
    for sinfo in serverinfo:
        server_choies.append((sinfo.ip, sinfo.ip + "(" + str(sinfo.hostremarks) + ")"))

    return core.SelectMultipleField(
        label='选择主机组' + fieldname + '主机',
        render_kw={'class': 'form-control selectpicker', 'multiple': "multiple"},
        choices=server_choies,
    )
