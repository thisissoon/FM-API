#!/usr/bin/env python
# encoding: utf-8

"""
fm.manage
=========

FM Management Command Scripts.
"""

import alembic

from flask.ext.migrate import Migrate, MigrateCommand, _get_config
from flask.ext.script import Manager, Server, prompt_bool
from fm import app
from fm.ext import db

app = app.create()

manager = Manager(app)
migrate = Migrate(app, db)


@MigrateCommand.command
def reset():
    """ Reset the current DB
    """

    drop = prompt_bool('Drop all tables? All data will be lost...')
    if drop:
        db.drop_all()
        db.session.commit()

        config = _get_config(None)
        alembic.command.stamp(config, 'base')
        alembic.command.upgrade(config, 'head')


manager.add_command("runserver", Server(host='0.0.0.0'))
manager.add_command('db', MigrateCommand)


def run():
    """ Manager runner.
    """

    manager.run()


if __name__ == '__main__':
    run()
