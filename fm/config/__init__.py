#!/usr/bin/env python
# encoding: utf-8

"""
fm.config
=========

Helper utilities for access application configuration.
"""

from flask import current_app


class ConfigProxy(object):
    """ A simple class which allows attribute access to application config.
    """

    def __getattr__(self, name):
        value = current_app.config.get(name)
        if value is None:
            raise AttributeError

        return value
