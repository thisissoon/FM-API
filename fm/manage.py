#!/usr/bin/env python
# encoding: utf-8

"""
fm.manage
=========

FM Management Command Scripts.
"""

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from fm import app
from fm.ext import db

app = app.create()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def runserver(ssl=False, host='0.0.0.0', port=5000):
    """ Customised run server function so we can run the development server
    with custom arguments.
    """

    kwagrs = {
        'host': host,
        'port': int(port)
    }

    if ssl:
        kwagrs['ssl_context'] = 'adhoc'

    app.run(**kwagrs)


def run():
    """ Manager runner.
    """

    manager.run()


if __name__ == '__main__':
    run()
