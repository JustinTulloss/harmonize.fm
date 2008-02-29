from masterapp.tests import *
from masterapp import model

class TestPlayerController(TestController):
    def test_index(self):
        """
        Testing <root>/player
        """
        response = self.app.get(url_for(controller='player'))
        # Test response...
        assert response.c.profile != None
        assert 'Rubicon Web Player' in response

    def test_get_data(self):
        """
        Testing <root>/player/get_data
        """
        """
        # Test that failure is returned on bad invocation
        response = self.app.get(url_for(
            controller='player', 
            action='get_data'
        ))
        assert '"success": false' in response
        """

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
            yield self.check_metadata, type

    def check_metadata(self, type):
        """
        Testing the different types of data that can be fetched
        """
        print "Testing %s" % type
        response = self.app.get(url_for(
            controller='player', 
            action='get_data'
        ), params={'type': type })
        assert '"success": true' in response, \
            "%s did not return success" % type
        
    def test_get_song_url(self):
        """
        Testing <root>/get_song_url/<songid>
        """
        response = self.app.get(url_for(
            controller='player',
            action = 'get_song_url',
            id = 7
        ))

        assert response.session.has_key('playing') == True,\
            "file being played not inserted into session as expected"
        assert 'music.rubiconmusicplayer.com' in response, \
            "Incorrect url was returned"

        # Now we'll mark a particular file as completely consumed (should die)
        files=model.Session.query(model.File).\
            filter(model.File.songid == 8).all()
        not_friend = model.Session.query(model.User).\
            filter(model.User.fbid == 1906978).first()
        for file in files:
            g.usedfiles[(file.id, file.ownerid)] = file.owners

        response = self.app.get(url_for(
            controller='player',
            action = 'get_song_url',
            id = 8
        ))
        assert 'false' in response, \
            "file was found when it should not have been"
