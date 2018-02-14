#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

mod = Blueprint('home', __name__)


@mod.route('/')
def index():
    return render_template('home/index.html')
