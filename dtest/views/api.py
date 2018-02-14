#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request

import json, time
from dtest.app.actions.utils import parsexml, signature

mod = Blueprint('api', __name__, url_prefix='/api')


@mod.route('/opensite')
def opensite():
    return render_template('api/opensite.html')


@mod.route('/open', methods=['GET', 'POST'])
def open():
    apiname = request.form['apiname']
    print(apiname)
    return json.dumps(parsexml.getapiparams(apiname))


@mod.route('/opensite_launch', methods=['GET', 'POST'])
def opensite_launch():

    consumer_key = request.form['consumer_key']
    print(consumer_key)
    consumer_secret = request.form['consumer_secret']
    t = int(time.time())
    params = {
        "consumer_key": consumer_key,
        "timestamp": t,
        "geo": "121.297721,31.821218"
    }

    url = "https://opensite.ele.me/api/launch/"
    url = signature.gen_sig(url, params, consumer_secret)
    print(url)
    return url

