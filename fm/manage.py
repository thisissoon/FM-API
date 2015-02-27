#!/usr/bin/env python
# encoding: utf-8

"""
fm.manage
=========

FM Management Command Scripts.
"""

from flask.ext.script import Manager, Server
from fm import app

manager = Manager(app.create)
manager.add_command("runserver", Server(host='0.0.0.0'))


def run():
    """ Manager runner.
    """

    manager.run()


if __name__ == '__main__':
    run()
