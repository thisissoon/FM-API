import os

bind = '{0}:{1}'.format(
    os.environ.get('GUNICORN_HOST', 'localhost'),
    os.environ.get('GUNICORN_PORT', ':5000'))
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
