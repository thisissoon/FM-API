FROM debian:wheezy

ADD https://apt.mopidy.com/mopidy.gpg /mopidy.gpg
ADD https://apt.mopidy.com/mopidy.list /etc/apt/sources.list.d/mopidy.list

RUN cat /mopidy.gpg | apt-key add -

RUN apt-get update && apt-get install -y \
        python-dev \
        python-pip \
        libffi-dev \
        libspotify-dev \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

WORKDIR /fm

ADD install.reqs /fm/install.reqs

RUN pip install -r install.reqs

EXPOSE 5000

ADD . /fm

RUN python setup.py install
