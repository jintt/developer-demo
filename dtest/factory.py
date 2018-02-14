#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import pkgutil
import traceback

from flask import Flask, render_template, Blueprint, url_for
from flask_debugtoolbar import DebugToolbarExtension

from dtest import settings, views


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    setup_error_handler(app)
    setup_debug_tool_bar(app)
    register_blueprints(app)
    config_filter(app)
    config_injects(app)

    return app


def config_injects(app):
    @app.context_processor
    def inject_settings():
        return dict(settings=settings)


def config_filter(app):
    @app.template_filter('get_url')
    def get_url(s):
        s = s.split('?')
        args = {j[0]: j[1] for j in
                [i.split('=') for i in (s[1] if len(s) > 1 else '').split('&')
                 if i]}
        return url_for(s[0], **args)

    @app.template_filter('is_list')
    def do_is_list(s):
        return isinstance(s, list)


def register_blueprints(app):
    rv = []
    for _, name, ispkg in pkgutil.iter_modules(views.__path__):
        m = importlib.import_module('.%s' % name, views.__name__)
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv


def setup_debug_tool_bar(app):
    toolbar = DebugToolbarExtension(app)


def setup_error_handler(app):
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.info('404 %s' % repr(e))
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def page_not_found(e):
        app.logger.info('404 %s' % repr(e))
        return render_template('errors/404.html'), 404

    @app.errorhandler(Exception)
    def page_error(e):
        app.logger.error('500 %s' % repr(e))
        traceback.print_exc()
        return render_template('errors/500.html'), 500
