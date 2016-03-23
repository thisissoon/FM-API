# Third Party Libs
from tests.factories.spotify import TrackFactory

# First Party Libs
from fm.serializers.spotify import TrackSerializer


class TestTrackSerializer(object):

    def should_populate_artists_name(self):
        track = TrackFactory()
        serialized = TrackSerializer().serialize(track)
        assert serialized['artists'][0]['name'], 'artist name is empty'
