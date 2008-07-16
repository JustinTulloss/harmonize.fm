from masterapp.tests import *
from masterapp.lib.fakefacebook import friends, friends_info
#from masterapp import model
import simplejson

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

        #Test a friend's playlist
        friend = generate_fake_user(friends[0])
        playlist = generate_fake_playlist(friend, 20)
        response = self.app.post(
            url_for(
                controller = 'metadata',
                action = 'songs'), 
            params={
                'friend': friend.id,
                'playlist': playlist.id
            }
        )
        data = simplejson.loads(response.body)['data']
        assert len(data) == 20, 'Not all playlist songs returned'

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
        friend = generate_fake_user(friends[0])
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'friends',
        ))
        assert '"Friend_id": %s' % friend.id in response.body,\
            "Did not return my friends"
        assert '"type": "friend"' in response.body,\
            "Did not send back correct type"

    def test_album(self):
        """
        Testing /metadata/album/<albumid>
        """
        # Test illegit
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'album',
            id = None
        ), status = 400)

        # Test my album
        song = generate_fake_song(self.user)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'album',
            id = song.albumid
        ))
        assert song.album.title in response.body,\
            "did not return my album"

        # Test friend's album
        friend = generate_fake_user(friends[0])
        song = generate_fake_song(friend)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'album',
            id = song.albumid
        ), params={'friend': friend.id})
        assert song.album.title in response.body,\
            "did not return friend's album"
        data = simplejson.loads(response.body)['data']
        assert data[0]['Friend_id'] == friend.id

    def test_playlist(self):
        """
        Testing /metadata/playlist/<playlistid>
        """
        # Test illegit
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'playlist',
            id = None
        ), status = 400)

        # Test my album
        playlist = generate_fake_playlist(self.user)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'playlist',
            id = playlist.id
        ))
        assert playlist.name in response.body,\
            "did not return my playlist"

        # Test friend's playlist (can't get to a friend's playlist)
        friend = generate_fake_user(friends[0])
        playlist = generate_fake_playlist(friend)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'playlist',
            id = playlist.id
        ), params={'friend': friend.id})
        assert playlist.name in response.body,\
            "did not return friend's playlist"
        data = simplejson.loads(response.body)['data']
        assert data[0]['Friend_id'] == friend.id

    def test_song(self):
        """
        Testing /metadata/song/<songid>
        """
        # Test illegit
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'song',
            id = None
        ), status = 400)
        
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'song',
            id = '124'
        ), status = 404)

        # Test my song
        song = generate_fake_song(self.user)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'song',
            id = song.id
        ))
        assert song.title in response.body,\
            "did not return my playlist"

        # Test friend's song
        friend = generate_fake_user(friends[0])
        song = generate_fake_song(friend)
        response = self.app.post(url_for(
            controller = 'metadata',
            action = 'song',
            id = song.id
        ), params={'friend': friend.id})
        assert song.title in response.body,\
            "did not return friend's playlist"
        data = simplejson.loads(response.body)['data']
        assert data[0]['Friend_id'] == friend.id

    def test_next_radio_song(self):
        """
        Testing /metadata/next_radio_song
        """
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'metadata',
            action = 'next_radio_song',
        ), status=404)
        
        #FIXME:I can't figure out how to make this work w/mockfacebook
        """
        friend = generate_fake_user(friends[0])
        song = generate_fake_song(friend)
        response = self.app.get(url_for(
            controller = 'metadata',
            action = 'next_radio_song',
        ))
        assert song.title in response.body,\
            "did not return friend's song"
        """

    def test_remove(self):
        """
        Testing /metadata/remove/<entity type>/<entityid>
        """
        # Test removing song
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'metadata',
            action = 'remove',
            type = 'song',
            id = song.id
        ))
        assert not model.Session.query(model.SongOwner).all(),\
            "did not delete song"

        # Test removing album
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'metadata',
            action = 'remove',
            type = 'album',
            id = song.albumid
        ))
        assert not model.Session.query(model.SongOwner).all(),\
            "did not delete song by album"

        # Test removing artist
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'metadata',
            action = 'remove',
            type = 'artist',
            id = song.artistid
        ))
        assert not model.Session.query(model.SongOwner).all(),\
            "did not delete song by arist"
