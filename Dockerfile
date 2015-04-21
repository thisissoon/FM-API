# Alpine is thin linux OS that weighs in at a few MB
FROM alpine:3.1

# Working Directory where all commands will be run from
WORKDIR /fm

# Install OS dependencies
RUN apk add --update \
    build-base \
    postgresql-dev \
    git \
    python \
    python-dev \
    py-pip \
    libevent-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*

# Set 5000 to be the default exposed port
EXPOSE 5000

# Install the Requirements via pip - Copying 1 file is cached
COPY ./REQUIREMENTS /fm/REQUIREMENTS
RUN pip install -r REQUIREMENTS

# Entry point - Runs the Gunicorn Server by Defult - WSGI entry point is dms/wsgi.py
# Enironment variables can be used to to set the Host / Port / Workers and Settings Modules
CMD gunicorn \
    -b $GUNICORN_HOST:$GUNICORN_PORT \
    -w $GUNICORN_WORKERS \
    -e DMS_SETTINGS_MODULE=$DMS_SETTINGS_MODULE \
    fm.wsgi:app

# Always Copy Files Last as everything that follows this will not be cached by docker
COPY . /fm
