#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify

from dtest.app.actions.utils.jenkins_api import jenkins_tools
import json

mod = Blueprint('uiauto', __name__, url_prefix='/uiauto')

jenkins_build_name = "H5 UI"

@mod.route('/uimain', methods=['GET', 'POST'])
def uimain():
    jenkins_api = jenkins_tools()
    build_list = jenkins_api.get_build_list("H5 UI")
    is_running = jenkins_api.is_job_running("H5 UI")
    running_status = ""
    if is_running:
        running_status = "Build is running."

    failed = [3,4,6,1,0,1,2,3,4,3,3,3,3,6,1,0,0,0,0,0]
    succ = [13,14,16,11,10,11,12,13,14,13,13,13,13,16,11,10,10,10,10,10]
    total = [13,14,16,11,10,11,12,13,14,13,13,13,13,16,11,10,10,10,10,10]
    builds = ['#60','#61','#62','#63','#64','#65','#66','#67','#68','#69','#70','#71','#72','#73','#74','#75','#76']
    # chartdata = {
    #     "failed":failed,
    #     "succ":succ,
    #     "total":total,
    #     "builds":builds
    # }
    chartdata = jenkins_api.chartdata
    return render_template('uiauto/uimain.html', build_list=build_list, running_status=running_status, chartdata = chartdata)

@mod.route('/build_project', methods=['GET', 'POST'])
def build_project():
    env = request.values.get("env")
    jenkins_build_name = "H5 UI"
    if env == "review":
        jenkins_build_name = "H5 UI review"

    jenkins_api = jenkins_tools()
    jenkins_api.project_built(jenkins_build_name)
    running_status = "Build is running."
    return jsonify(running_status=running_status)



@mod.route('/stop_build', methods=['GET', 'POST'])
def stop_build():
    jenkins_api = jenkins_tools()
    jenkins_api.stop_build(jenkins_build_name)
    running_status = "Build is stopped"
    return jsonify(running_status=running_status)


@mod.route('/build_status', methods=['GET'])
def build_status():
    jenkins_api = jenkins_tools()
    build_status = jenkins_api.is_job_running(jenkins_build_name)
    return jsonify(build_status=build_status)

