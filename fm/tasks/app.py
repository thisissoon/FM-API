#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.app
============

Celery Application Entry Point.
"""

from fm.app import create
from fm.tasks import Celery


celery = Celery().init_app(create())
