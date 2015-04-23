#!/usr/bin/env python
# encoding: utf-8

"""
tests.factories.user
====================

SQLAlchemy Factories for User models.
"""

# Standard Libs
import json

# Third Pary Libs
import factory
from factory import fuzzy

# First Party Libs
from fm.models.user import User
from tests.factories import UUID4, Factory


class UserFactory(Factory):
    """ Artist Model Factory
    """

    class Meta:
        model = User

    id = UUID4()
    gplus_id = fuzzy.FuzzyInteger(1000, 10000)
    oauth2_credentials = factory.LazyAttribute(lambda o: json.dumps({
        'foo': 'bar'
    }))
    email = factory.LazyAttribute(lambda o: u'{0}@thisissoon.com'.format(
        o.given_name))
    given_name = fuzzy.FuzzyText(length=6)
    family_name = fuzzy.FuzzyText(length=8)
    display_name = fuzzy.FuzzyText(length=6)
    avatar_url = factory.LazyAttribute(lambda o: u'http://{0}.jpg'.format(
        o.given_name))
