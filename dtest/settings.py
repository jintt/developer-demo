#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

SECRET_KEY = 'i-like-flask'

SESSION_COOKIE_NAME = 'dtest'
SITE_NAME = u'测试平台'
DB_CONNECT_STRING = 'mysql+mysqldb://root:password@mysql:3306/dtest?charset=utf8'
DB_SQL_ECHO = True

# debug toolbar
DEBUG = True
DEBUG_TB_PROFILER_ENABLED = True


menus = [

    (u'接口自动化', 'fa fa-edit',
        [(u'opensite', 'api.opensite', ['api.opensite']),
         ],
     ['api.open', 'api.opensite']
     ),

    (u'UI自动化', 'fa fa-desktop',
        [(u'H5', 'uiauto.uimain', ['uiauto.uimain']),
         ],
     ['uiauto.uimain']
     )
]

if os.environ.get('ENV') == 'prod':
    DEBUG = False
    DEBUG_TB_PROFILER_ENABLED = False
