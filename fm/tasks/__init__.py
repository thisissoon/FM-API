#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks
========

Celery application setup.
"""


from celery import Celery


def celery():
    """ Ceeley application factory.
    """

    from fm.app import create
    app = create()

    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):

        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    if not celery.conf.get('ALWAYS_EAGER'):
        celery.Task = ContextTask

    return celery
