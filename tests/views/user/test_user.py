#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.user.test_user
==========================

Unit tests for the ``fm.views.user.UserView`` class.
"""

import uuid
import httplib

from flask import url_for
from fm.ext import db
from fm.serializers.user import UserSerializer
from tests.factories.user import UserFactory


class TestUserGet(object):

    def must_be_valid_uuid(self):
        url = url_for('users.user', pk='foo')
        response = self.client.get(url)

        assert response.status_code == 404

    def should_return_not_found(self):
        url = url_for('users.user', pk=unicode(uuid.uuid4()))
        response = self.client.get(url)

        assert response.status_code == 404

    def should_return_serialized_user(self):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        url = url_for('users.user', pk=user.id)
        response = self.client.get(url)

        expected = UserSerializer().serialize(user)

        assert response.status_code == 200
        assert response.json == expected

    def test_user_has_authorized_on_spotify(self):
        user = UserFactory()
        user.spotify_id = '54774645'

        db.session.add(user)
        db.session.commit()

        url = url_for('users.user', pk=user.id)
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.json['spotify_playlists'].startswith('http')

    def test_user_has_not_authorized_on_spotify(self):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        url = url_for('users.user', pk=user.id)
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.json['spotify_playlists'] is None

    def test_spotify_playlist_returns_404_for_unauthorized_on_spotify(self):
        user = UserFactory()
        db.session.add(user)
        db.session.commit()

        response = self.client.get(url_for('users.user_playlists', pk=user.id))
        assert response.status_code == httplib.NO_CONTENT
