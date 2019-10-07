# -*- coding: utf-8 -*-
"""
create by caijinxu on 2018/12/28
"""
from app.web import web
from flask import request, render_template, redirect, url_for, flash, current_app
from app.models.cmdb import ServerInfo, Scan
from app.forms.autoscan import IpForm
from app.libs.scanip import Scanip
from app.libs.task.scanip import run_trylogin
import json
from flask_login import login_required
from app.view_models.ansible_view import scanaddcmdb

__author__ = 'caijinxu'


@web.route('/autoscan', methods=['POST', 'GET'])
@login_required
def autoscan():
    form = IpForm(request)

    if request.method == "GET":
        ipinfo = Scan.query.filter_by().all()
        return render_template('scanip.html', form=form, infos=ipinfo)
    if form.validate():
        iplist = form.ips.data.split(';')
        sc = Scanip(iplist)
        liveip = sc.get_nmapliveip()  # 输入IP中存活的IP地址
        infos = ServerInfo.query.filter(ServerInfo.ip.in_(liveip)).all()
        for info in infos:
            liveip.remove(info.ip)  # 清除存活IP中已在资产信息表的IP
        if liveip:
            flash("发现存活IP:" + json.dumps(liveip) + "稍后刷新页面")
            ip_loginfos = sc.trylogin(liveip)
            for ip_loginfo in ip_loginfos:
                run_trylogin(ip_loginfo['ip'], ip_loginfo['loginfolist'])
        else:
            flash("没有发现新IP")
    return redirect(url_for('autoscan.index_view'))


@web.route("/autoscan/addcmdb/", methods=["POST"])
@login_required
def addCMDB():
    if request.form.get('hostip'):
        hostip = request.form['hostip'].replace(' ', '').replace('\n', '')
        scanaddcmdb(hostip)
        return '1'
    flash("加入cmdb出错")
    return '1'

