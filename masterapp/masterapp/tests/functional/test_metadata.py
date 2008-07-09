from masterapp.tests import *
from masterapp.lib.fakefacebook import friends
#from masterapp import model

class TestMetadataController(TestModel):

    def test_index(self):
        """
        Testing /metadata
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
        ]
        for type in types:
            self.check_metadata(type)

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
        Testing /metadata/artists
        """
        # Test my own artist
        song = generate_fake_song(self.user)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'artists',
        ))
        assert song.artist.name in response.body,\
            "Did not return my artist"

        # Test a friend's artist
        friend = generate_fake_user(friends[0])
        song = generate_fake_song(friend)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'artists',
        ), params={'friend': friend.id})
        assert song.artist.name in response.body,\
            "Did not return my friend's artist"


    def test_songs(self):
        """
        Testing /metadata/songs
        """
        # Test my own song
        song = generate_fake_song(self.user)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'songs',
        ))
        assert song.title in response.body,\
            "Did not return my song"

        # Test a friend's song
        friend = generate_fake_user(friends[0])
        song = generate_fake_song(friend)
        response = self.app.post(
            url_for(
                controller = 'metadata',
                action = 'songs'), 
            params={
                'friend': friend.id,
                'album': song.albumid,
                'artist': song.artistid,
            }
        )
        assert song.title in response.body,\
            "Did not return my friend's song"

    def test_albums(self):
        """
        Testing /metadata/albums
        """
        # Test my own album
        song = generate_fake_song(self.user)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'albums',
        ))
        assert song.album.title in response.body,\
            "Did not return my album"

        # Test a friend's album
        friend = generate_fake_user(friends[0])
        song = generate_fake_song(friend)
        response = self.app.post(
            url_for(
                controller = 'metadata',
                action = 'albums'), 
            params={
                'friend': friend.id,
                'artist': song.artistid,
            }
        )
        assert song.album.title in response.body,\
            "Did not return my friend's album"

    def test_playlists(self):
        """
        Testing /metadata/playlists
        """
        # Test my own playlist
        playlist = generate_fake_playlist(self.user)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'playlists',
        ))
        assert playlist.name in response.body,\
            "Did not return my playlist"

        # Test a friend's playlist
        friend = generate_fake_user(friends[0])
        playlist = generate_fake_playlist(friend)
        response = self.app.post(
            url_for(
                controller = 'metadata',
                action = 'playlists'), 
            params={'friend': friend.id}
        )
        assert playlist.name in response.body,\
            "Did not return my friend's playlist"

    def test_friends(self):
        """
        Testing /metadata/friends
        """
        pass
