#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks
========

Celery application setup.

See Also
--------
* fm.tasks.app

"""


import celery


class Celery(object):
    """ Class for setting up celery with a given Flask application.
    """

    def __init__(self, app=None):
        """ Initialiser of the Celery instance. If an application is provieed
        it will call ``init_app``.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance
        """

        if app is not None:
            self.init_app(app)

    def __getattr__(self, name):
        """ Allows access to attributes on the Redis connection instance.

        Arguments
        ---------
        name : str
            Attribute name
        """

        if hasattr(self.celery, name):
            return getattr(self.celery, name)

        raise AttributeError

    def init_app(self, app):
        """ Initialise Celery for the Flask application from the application
        configuration.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance
        """

        # Create the Celery Application
        celery_app = celery.Celery(app.import_name)
        celery_app.conf.update(app.config)
        TaskBase = celery.Task

        # Custom task to ensure tasks a called with an application
        # context to allow for proper setup and teardown
        class ContextTask(TaskBase):

            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        # If we are in always eager mode then we don't need to alter the
        # task base class
        if not celery_app.conf.get('ALWAYS_EAGER'):
            celery_app.Task = ContextTask

        # Store the celery app on on this instance for access later
        self.celery = celery_app

        # Return the celery application
        return celery_app
