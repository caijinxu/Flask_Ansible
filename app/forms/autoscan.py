import IPy
from app.forms.base import BaseForm, DataRequired
from wtforms.fields import simple
from wtforms import validators
from wtforms import widgets
from wtforms.fields import core

class IpForm(BaseForm):
    """检查输入IP格式，多个直接以';'分隔"""
    ips = simple.StringField(
        label="扫描发现网段或IP登录信息",
        validators=[DataRequired()],
        widget=widgets.TextArea(),
        render_kw={"placeholder": "输入IP地址或IP地址段,以;隔开如：192.168.15.202;192.168.15.0/24", "rows": 3, 'class': 'form-control'}
    )
    def validate_ips(self, value):
        ip_list = value.data.split(';')
        for ip in ip_list:
            try:
                IPy.IP(ip)
            except Exception as e:
                raise validators.ValidationError(message='请输入正常的IP格式')

