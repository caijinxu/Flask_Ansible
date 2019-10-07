from app.web import web
from flask import request, render_template, redirect, url_for, flash, current_app
from app.forms.ansible import AdhocForm, TaskInfoForm, CreatePlayBookForm, EditPlayBookForm, DynamicGroupForm, get_selectfield
from app.models.ansible import PlayBook
from app.models.cmdb import ServerInfo
from app.models import db
from flask_login import login_required
from app.view_models.ansible_view import run_adhoc, run_playbook, get_pagination, format_output
from app.libs.db_connect import Mongo
from app.secure import MONGO_DATABASE, MONGO_ANSIBLE_COLLECTION
import pymongo
import json
import yaml


@web.route('/ansible/adhoc', methods=['GET', 'POST'])
@login_required
def adhoc():
    form = AdhocForm(request)
    if request.method == "POST" and form.validate():
        iplist = request.form.getlist('ip')
        work_uuid = run_adhoc(form, iplist)
        flash("任务执行ID：" + str(work_uuid))
        return redirect(url_for("web.history"))
    else:
        return render_template('ansible/adhoc.html', form=form)


@web.route('/ansible/history', methods=['GET'])
@login_required
def history():
    page = int(request.args.get("page", 1))
    pagelimit = 20

    m = Mongo()
    mdb = m.client[MONGO_DATABASE]
    findr = {}
    if request.args.get("mode"):
        if request.args['mode'] == "adhoc":
            findr['mode'] = "adhoc"
        elif request.args['mode'] == "playbook":
            findr['mode'] = "playbook"
    historytask = mdb[MONGO_ANSIBLE_COLLECTION].find(findr, {"mode": 1, "name": 1, "uuid": 1, "create_time": 1,
                                                     "describe": 1, "username": 1, "pattern": 1})\
        .sort("create_ts", pymongo.DESCENDING).skip(pagelimit*(page - 1)).limit(pagelimit)
    taskcounts = mdb[MONGO_ANSIBLE_COLLECTION].find(findr).count()
    pagination = get_pagination(taskcounts, pagelimit, page)
    return render_template("ansible/history.html", historytask=historytask, pageination=pagination)


@web.route("/ansible/history/details", methods=['GET'])
def historydetails():
    form = TaskInfoForm(request)
    if form.validate():
        m = Mongo()
        mdb = m.client[MONGO_DATABASE]
        taskinfo = mdb[MONGO_ANSIBLE_COLLECTION].find_one({"uuid": form.taskuuid.data})
        # print(type(taskinfo['detail']))
        if taskinfo:
            taskinfo = format_output(taskinfo)
            return render_template('ansible/historydetails.html', taskinfo=taskinfo)
        else:
            flash("没有查询到任务相关详情信息")
            return redirect(url_for('web.history'))
    else:
        flash("任务id错误")
        return redirect(url_for('web.history'))


@web.route("/ansible/playbook/create", methods=['GET', "POST"])
@login_required
def createplaybook():
    form = CreatePlayBookForm(request)
    if request.method == "POST" and form.validate():
        with db.auto_commit():
            playbook = PlayBook()
            playbook.name = form.name.data
            playbook.content = form.content.data
            playbook.remark = form.remark.data
            db.session.add(playbook)
        flash("添加剧本成功")
        return redirect(url_for('web.playbookcenter'))
    else:
        return render_template("ansible/playbook.html", form=form, title="新建PlayBook")


@web.route("/ansible/playbook/", methods=['GET'])
@login_required
def playbookcenter():
    playbook = PlayBook.query.filter_by().all()
    return render_template("ansible/playbooklist.html", playbook=playbook)


@web.route("/ansible/playbook/edit", methods=['GET', "POST"])
@login_required
def editplaybook():
    form = EditPlayBookForm(request)

    playbook = PlayBook.query.filter_by(name=form.name.data).first()
    if request.method == "POST" and form.validate():
        with db.auto_commit():
            playbook.content = form.content.data
            playbook.remark = form.remark.data
        flash("编辑剧本成功")
        return redirect(url_for('web.playbookcenter'))
    else:
        form.content.data = playbook.content
        form.remark.data = playbook.remark
        return render_template("ansible/playbook.html", form=form, title="编辑PlayBook")


@web.route("/ansible/playbook/run/", methods=['GET', "POST"])
@login_required
def runplaybook():
    class DynamicForm(DynamicGroupForm):
        pass
    if request.method == "GET":
        if request.args.get('name'):
            playbook = PlayBook.query.filter_by(name=request.args['name']).first()
            playbook_content = yaml.load(playbook.content, yaml.FullLoader)
            for hosts in playbook_content:
                if hosts.get('hosts'):
                    setattr(DynamicForm, hosts['hosts'], get_selectfield(hosts['hosts']))
            form = DynamicForm(request)
            print(dir(form))
            return render_template('ansible/playbook.html', form=form)
    else:
        playbook = PlayBook.query.filter_by(name=request.form['name']).first()
        playbook_content = yaml.load(playbook.content, yaml.FullLoader)
        group = {}
        for play in playbook_content:
            if play.get('hosts'):
                setattr(DynamicForm, play['hosts'], get_selectfield(play['hosts']))
                if not request.form.getlist(play['hosts']):
                    flash(play['hosts'] + '：请选择执行主机')

                    return redirect(url_for('web.runplaybook', name=request.form['name']))
                group[play['hosts']] = request.form.getlist(play['hosts'])
        form = DynamicForm(request)
        run_resulte = run_playbook(group, form, playbook.content)
        flash("执行PlayBook任务ID：" + run_resulte)
        return redirect(url_for("web.history"))
