#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.app
============

Celery Application Entry Point.
"""

# First Party Libs
from fm.app import create
from fm.tasks import Celery


celery = Celery(create())
