#!/usr/bin/env python
# encoding: utf-8

"""
fm.manage
=========

FM Management Command Scripts.
"""

from alembic import command
from flask.ext.migrate import Migrate, MigrateCommand, _get_config
from flask.ext.script import Manager, Server, prompt_bool
from fm import app
from fm.events.listener import listener
from fm.ext import db
from gevent.monkey import patch_all


app = app.create()

manager = Manager(app)
migrate = Migrate(app, db)


@manager.command
def runeventlistener():
    """ Run the Redis Event Listener. This will spawn a Gevent Greenlet.
    """

    patch_all()

    try:
        listener()
    except KeyboardInterrupt:
        print 'Exited'


@MigrateCommand.command
def reset():
    """ Reset the current DB
    """

    drop = prompt_bool('Drop all tables? All data will be lost...')
    if drop:
        db.drop_all()
        db.session.commit()

        config = _get_config(None)
        command.stamp(config, 'base')
        command.upgrade(config, 'head')


manager.add_command("runserver", Server(host='0.0.0.0'))
manager.add_command('db', MigrateCommand)


def run():
    """ Manager runner.
    """

    manager.run()


if __name__ == '__main__':
    run()
