from masterapp.tests import *
from masterapp import model

class TestMetadataController(TestController):

    def test_index(self):
        """
        Testing <root>/metadata
        """
        """
        # Test that failure is returned on bad invocation
        response = self.app.get(url_for(
            controller='metadata', 
            action='index'
        ))
        assert '"success": false' in response, \
            "Asking for metadata without type did not fail"

        #Test fetching all of each particular type
        types = [
            'artist',
            'album',
            'song',
            'friend',
            'playlist',
            'playlistsong'
        ]
        for type in types:
            self.check_metadata(type)
        """

    def check_metadata(self, type):
        """
        Testing the different types of data that can be fetched
        """
        print "Testing %s" % type
        response = self.app.get(url_for(
            controller='metadata', 
            action='index'
        ), params={'type': type })
        assert '"success": true' in response, \
            "%s did not return success" % type

    def test_artists(self):
        """
        Testing <root>/metadata/artists
        """
        pass

    def test_songs(self):
        """
        Testing <root>/metadata/artists
        """
        pass

    def test_albums(self):
        """
        Testing <root>/metadata/albums
        """
        pass

    def test_playlists(self):
        """
        Testing <root>/metadata/playlists
        """
        pass

    def test_playlistsongs(self):
        """
        Testing <root>/metadata/playlistsongs
        """
        pass

    def test_friends(self):
        """
        Testing <root>/metadata/friends
        """
        pass
        
 
