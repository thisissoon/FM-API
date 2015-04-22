# Alpine is thin linux OS that weighs in at a few MB
FROM ubuntu:14.04

# pip Installer
ADD https://bootstrap.pypa.io/get-pip.py /get-pip.py

# Working Directory where all commands will be run from
WORKDIR /fm

# Install OS dependencies
RUN apt-get update -y && apt-get install --no-install-recommends -y -q \
        build-essential \
        libpq-dev \
        libevent-dev \
        libffi-dev \
        python \
        python-dev \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

# Install Pip
RUN chmod +x /get-pip.py
RUN python /get-pip.py

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
