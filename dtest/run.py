#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dtest import factory
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware


app = DispatcherMiddleware(factory.create_app())

if __name__ == "__main__":
    app_options = {'use_reloader': True, 'use_debugger': False}
    run_simple('0.0.0.0', 5000, app, **app_options)
