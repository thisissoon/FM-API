#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue
=============================

Unit tests for the ``fm.views.player.QueueView`` class.
"""

import unittest

from fm.app import create
from fm.ext import db
from tests.factories.spotify import TrackFactory


class TestGet(unittest.TestCase):
    """Player Queue: GET
    """

    def setUp(self):
        self.app = create()

    def test_foo(self):
        track = TrackFactory()

        db.session.add(track)
        db.session.commit()

        from nose.tools import set_trace; set_trace()
