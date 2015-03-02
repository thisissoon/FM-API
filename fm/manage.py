#!/usr/bin/env python
# encoding: utf-8

"""
fm.manage
=========

FM Management Command Scripts.
"""

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager, Server
from fm import app
from fm.ext import db

app = app.create()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("runserver", Server(host='0.0.0.0'))
manager.add_command('db', MigrateCommand)


def run():
    """ Manager runner.
    """

    manager.run()


if __name__ == '__main__':
    run()
