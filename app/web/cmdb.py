import json
from app.web import web
from flask import request, render_template, redirect, url_for, flash, current_app
from app.models import db
from flask_login import login_required
from app.models.cmdb import ServerInfo, Scan
from app.forms.autoscan import IpForm
from app.libs.scanip import Scanip
from app.libs.task.scanip import run_trylogin
from app.view_models.ansible_view import refresh_server, scanaddcmdb


@web.route("/cmdb/refresh/", methods=['POST'])
@login_required
def refresh_cmdb():
    if request.form.get("ip"):
        ip = request.form["ip"]
        server = ServerInfo.query.filter_by(ip=ip.replace(' ', '').replace('\n', '')).all()
        if not server:
            flash("刷新配置信息出错，没有找到IP地址修改配置")
            return ""
        else:
            result = refresh_server(server)
            if not result:
                flash("没有获取到相应的fatcs信息")
                return ""
            for info in result:
                for ser in server:
                    if ser.ip == info['ip']:
                        with db.auto_commit():
                            i = info
                            i.pop('ip')
                            ser.set_attrs(info)
                        flash(ser.ip + "：刷新配置成功")
            return ""
    flash("刷新配置信息出错")
    return ""


@web.route('/autoscan', methods=['POST'])
@login_required
def autoscan():
    form = IpForm(request)
    if form.validate():
        iplist = form.ips.data.split(';')
        sc = Scanip(iplist)
        liveip = sc.get_nmapliveip()  # 输入IP中存活的IP地址
        infos = ServerInfo.query.filter(ServerInfo.ip.in_(liveip)).all()
        for info in infos:
            liveip.remove(info.ip)  # 清除存活IP中已在资产信息表的IP
        if liveip:
            flash("发现存活IP:" + json.dumps(liveip) +"稍后刷新页面")
            ip_loginfos = sc.trylogin(liveip)
            for ip_loginfo in ip_loginfos:
                run_trylogin(ip_loginfo['ip'], ip_loginfo['loginfolist'])
        else:
            flash("没有发现新IP")
    return redirect(url_for('autoscan.index_view'))


@web.route("/cmdb/addcmdb/", methods=["POST"])
@login_required
def addCMDB():
    if request.form.get('hostip'):
        hostip = request.form['hostip'].replace(' ', '').replace('\n', '')
        scanaddcmdb(hostip)
        return '1'
    flash("加入cmdb出错")
    return '1'


@web.route('/', methods=["GET"])
def index():
    return redirect(url_for('autoscan.index_view'))