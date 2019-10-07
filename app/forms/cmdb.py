from app.forms.base import BaseForm, DataRequired
from wtforms.fields import simple
from wtforms import validators
from wtforms import StringField
from wtforms import widgets


class EditCMDB(BaseForm):
    ip = StringField(
        label="IP地址",
        validators=[DataRequired()],
    )
    hostremarks = StringField(
        label="备注名称",
        validators=[DataRequired(), validators.length(2, 10, "长度最少2位，最多10位")],
    )


