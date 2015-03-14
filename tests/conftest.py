import json
import pytest

from fm.app import create
from fm.ext import db as _db


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
    _app = create()
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
