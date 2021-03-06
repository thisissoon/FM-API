#!/usr/bin/env python
# encoding: utf-8

"""
fm.manage
=========

FM Management Command Scripts.
"""
# Third Party Libs
import alembic
from flask.ext.migrate import Migrate, MigrateCommand, _get_config
from flask.ext.script import Manager, prompt_bool

# First Party Libs
from fm import app
from fm.events.listener import listener
from fm.ext import db


app = app.create()

manager = Manager(app)
migrate = Migrate(app, db)


@manager.command
def runeventlistener():
    """ Run the Redis Event Listener. This will spawn a Gevent Greenlet.
    """

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
        alembic.command.stamp(config, 'base')
        alembic.command.upgrade(config, 'head')


@manager.command
def runserver(ssl=False, host='0.0.0.0', port=5000, migrate=False):
    """ Customised run server function so we can run the development server
    with custom arguments.
    """

    # Run migrations before server start
    if migrate:
        config = _get_config(None)
        alembic.command.upgrade(config, 'head')

    # Host / Port Config
    kwagrs = {
        'host': host,
        'port': int(port)
    }

    # Run with SSL?
    if ssl:
        kwagrs['ssl_context'] = 'adhoc'

    app.run(**kwagrs)


manager.add_command('db', MigrateCommand)


def run():
    """ Manager runner.
    """

    manager.run()


if __name__ == '__main__':
    run()
