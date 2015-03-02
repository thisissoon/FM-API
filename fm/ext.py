#!/usr/bin/env python
# encoding: utf-8

"""
fm.ext
======

Flask Application Extension Instantiation.
"""

from fm.db.sqla import FMSQLAlchemy
from flask.ext.via import Via
from fm.config import ConfigProxy
from fm.db.nosql import Redis
from fm.tasks import celery as _celery
from werkzeug import LocalProxy

# Celery
celery = LocalProxy(lambda: _celery())

# Flask-Via for Routing Modules
via = Via()

# Redis -  Stores application state
redis = Redis()

# Easier config access
config = LocalProxy(lambda: ConfigProxy())

# SQLAlchemy
db = FMSQLAlchemy()
