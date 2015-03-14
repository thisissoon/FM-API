#!/usr/bin/env python
# encoding: utf-8

"""
FM Player
=========

API Iterface to the physical FM player.
"""

# Temporary patch for issue reported here:
# https://groups.google.com/forum/#!topic/nose-users/fnJ-kAUbYHQ
import multiprocessing  # noqa
import os
import sys

from setuptools import setup, find_packages

root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(root, 'fm'))

import fm  # noqa


def read_requirements(filename):
    """ Read requirements file and process them into a list
    for usage in the setup function.

    Arguments
    ---------
    filename : str
        Path to the file to read line by line

    Returns
    --------
    list
        list of requirements::

            ['package==1.0', 'thing>=9.0']
    """

    requirements = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#') or line == '':
                continue
            requirements.append(line)
    requirements.reverse()
    return requirements

# Get current working directory

try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

# Change to current working directory

if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

# Requirements

INSTALL_REQS = read_requirements('install.reqs')
TESTING_REQS = read_requirements('test.reqs')
DEVELOP_REQS = TESTING_REQS + read_requirements('develop.reqs')

# Setup

setup(
    name='FM-API',
    version=fm.__version__,
    author=fm.__author__,
    author_email=fm.__author_email__,
    url='https://bitbucket.org/soon_/do-it-core',
    description='Core Do-It code base containing models and api views.',
    long_description=open('README.rst').read(),
    packages=find_packages(
        exclude=[
            'tests'
        ]),
    data_files=[('', ['VERSION'])],
    include_package_data=True,
    zip_safe=False,
    # Dependencies
    install_requires=INSTALL_REQS,
    extras_require={
        'develop': DEVELOP_REQS
    },
    # Testing
    tests_require=TESTING_REQS,
    # Entry points, for example Flask-Script
    entry_points={
        'console_scripts': [
            'manage.py = fm.manage:run',
        ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'])
