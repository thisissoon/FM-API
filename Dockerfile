FROM debian:wheezy

ADD https://bootstrap.pypa.io/get-pip.py /get-pip.py

RUN apt-get update && apt-get install -y \
        build-essential \
        libpq-dev \
        python-dev \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN chmod +x /get-pip.py
RUN /get-pip.py

WORKDIR /fm
COPY . /fm

RUN pip install -r install.reqs

EXPOSE 5000

RUN python setup.py install

CMD gunicorn -b $GUNICORN_HOST:$GUNICORN_PORT -e FM_SETTINGS_MODULE=$FM_SETTINGS_MODULE -w $GUNICORN_WORKERS fm.wsgi:app
