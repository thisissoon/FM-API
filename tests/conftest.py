#!/usr/bin/env python
# encoding: utf-8

"""
tests.conftest
==============

PyTest Configuration
"""

# Standard Libs
import json

# Third Party Libs
import pytest
from flask import g
from tests.factories.user import UserFactory

# First Party Libs
from fm.app import create
from fm.ext import db as _db


_app = create()  # Create Application Instance


class Response(object):

    @property
    def json(self):
        return json.loads(self.data)


class InjectContentTypeHeader(object):
    """ All test client requests should send Content-Type: appliccation/json
    with each request. This is just for convenience.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if not environ['REQUEST_METHOD'] == 'GET' \
                and environ['CONTENT_TYPE'] == '':
            environ['CONTENT_TYPE'] = 'application/json'

        return self.app(environ, start_response)


@pytest.yield_fixture(scope='session')
def app(request):
    _response_class = _app.response_class
    _app.response_class = type("Response", (Response, _app.response_class), {})
    _app.wsgi_app = InjectContentTypeHeader(_app.wsgi_app)

    yield _app

    _app.response_class = _response_class


@pytest.yield_fixture(scope='session')
def db(request, app):
    _db.app = app

    _db.drop_all()
    _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()
    _db.create_all()


@pytest.yield_fixture(scope='function', autouse=True)
def client(request, app):
    _test_client_class = app.test_client_class

    request.instance.client = app.test_client()

    yield request.instance.client
    del request.instance.client

    app.test_client_class = _test_client_class


@pytest.yield_fixture(scope='function', autouse=True)
def session(request, db, app):
    with app.test_request_context():
        request.instance.app = app

        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.close()
        db.session.remove()
        _get_binds = db.get_binds

        def get_binds(app):
            return {}

        db.get_binds = get_binds
        session = db.create_scoped_session({
            'bind': connection
        })
        db.session = session

        yield session

        del request.instance.app

        db.get_binds = _get_binds
        transaction.rollback()
        connection.close()
        session.remove()


class PatchCleanup(object):

    def __init__(self):
        self.patches = []

    def addPatchCleanup(self, patch):
        self.patches.append(patch)

    def cleanUpPatches(self):
        for p in reversed(self.patches):
            p.stop()

        self.patches[:] = []


@pytest.yield_fixture(scope='function', autouse=True)
def cleanup(request, db, app):
    cleanup = PatchCleanup()
    request.instance.addPatchCleanup = cleanup.addPatchCleanup

    yield cleanup

    cleanup.cleanUpPatches()


@pytest.fixture()
def authenticated(request, db, app):
    if not getattr(request.instance, 'unauthenticated', False):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        g.user = user


@pytest.fixture()
def unauthenticated(request, db, app):
    request.instance.unauthenticated = True
