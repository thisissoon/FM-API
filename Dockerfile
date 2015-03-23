FROM debian:jessie

ADD https://bootstrap.pypa.io/get-pip.py /get-pip.py

RUN apt-get update && apt-get install -y \
        build-essential \
        git \
        python-dev \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        libc6-dev \
        libevent-dev \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN chmod +x /get-pip.py
RUN python /get-pip.py

RUN pip install Cython==0.22

WORKDIR /fm

COPY . /fm
RUN python setup.py install

EXPOSE 5000

CMD gunicorn -b $GUNICORN_HOST:$GUNICORN_PORT -e FM_SETTINGS_MODULE=$FM_SETTINGS_MODULE -w $GUNICORN_WORKERS fm.wsgi:app
