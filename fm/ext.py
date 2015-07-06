#!/usr/bin/env python
# encoding: utf-8

"""
fm.ext
======

Flask Application Extension Instantiation.
"""
# Third Party Libs
from flask.ext.via import Via
from werkzeug import LocalProxy

# First Party Libs
from fm.config import ConfigProxy
from fm.db.nosql import Redis
from fm.db.sqla import FMSQLAlchemy
from fm.tasks import Celery


# Celery
celery = Celery()

# Flask-Via for Routing Modules
via = Via()

# Redis -  Stores application state
redis = Redis()

# Easier config access
config = LocalProxy(lambda: ConfigProxy())

# SQLAlchemy
db = FMSQLAlchemy()
