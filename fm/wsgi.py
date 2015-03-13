#!/usr/bin/env python
# encoding: utf-8

"""
fm.wsgi
=======

WSGI App Entry Point
"""

from fm.app import create

app = create()
