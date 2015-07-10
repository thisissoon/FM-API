from __future__ import division

# Third Party Libs
from sqlalchemy import desc
from sqlalchemy.orm import lazyload
from sqlalchemy.sql import func

# First Party Libs
from fm.models.spotify import (
    Album,
    Artist,
    ArtistAlbumAssociation,
    ArtistGenreAssociation,
    Genre,
    PlaylistHistory,
    Track
)
from fm.models.user import User


def most_active_djs(since=None, until=None):
    query = User.query \
        .with_entities(User, func.count(User.id).label('count')) \
        .join(PlaylistHistory) \
        .group_by(User.id) \
        .order_by(desc('count'))
    if since:
        query = query.filter(PlaylistHistory.created >= since)
    if until:
        query = query.filter(PlaylistHistory.created <= until)
    return query


def total_play_time_per_user(since=None, until=None):
    query = User.query \
        .with_entities(User, func.sum(Track.duration).label('sum')) \
        .join(PlaylistHistory) \
        .join(Track) \
        .group_by(User.id) \
        .order_by(desc('sum'))
    if since:
        query = query.filter(PlaylistHistory.created >= since)
    if until:
        query = query.filter(PlaylistHistory.created <= until)
    return query


def total_play_time(since=None, until=None):
    query = Track.query.with_entities(
        func.sum(Track.duration).label('sum')
    ).join(PlaylistHistory)
    if since:
        query = query.filter(PlaylistHistory.created >= since)
    if until:
        query = query.filter(PlaylistHistory.created <= until)
    return query


def total_plays(since=None, until=None):
    query = PlaylistHistory.query
    if since:
        query = query.filter(PlaylistHistory.created >= since)
    if until:
        query = query.filter(PlaylistHistory.created <= until)
    return query


def most_played_tracks(since=None, until=None):
    query = Track.query \
        .options(lazyload(Track.album)) \
        .with_entities(Track, func.count(Track.id).label('count')) \
        .join(PlaylistHistory) \
        .group_by(Track.id) \
        .order_by(desc('count'))
    if since:
        query = query.filter(PlaylistHistory.created >= since)
    if until:
        query = query.filter(PlaylistHistory.created <= until)
    return query


def most_played_artists(since=None, until=None):
    query = Artist.query \
        .with_entities(Artist, func.count(Artist.id).label('count')) \
        .join(ArtistAlbumAssociation) \
        .join(Album) \
        .join(Track) \
        .join(PlaylistHistory) \
        .group_by(Artist.id) \
        .order_by(desc('count'))
    if since:
        query = query.filter(PlaylistHistory.created >= since)
    if until:
        query = query.filter(PlaylistHistory.created <= until)
    return query


def most_played_genres(since=None, until=None):
    query = Genre.query \
        .with_entities(Genre, func.count(Genre.id).label('count')) \
        .join(ArtistGenreAssociation) \
        .join(Artist) \
        .join(ArtistAlbumAssociation) \
        .join(Album) \
        .join(Track) \
        .join(PlaylistHistory) \
        .group_by(Genre.id) \
        .order_by(desc('count'))
    if since:
        query = query.filter(PlaylistHistory.created >= since)
    if until:
        query = query.filter(PlaylistHistory.created <= until)
    return query
