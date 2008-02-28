from masterapp.tests import *
from masterapp import model

class TestPlayerController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='player'))
        # Test response...
        assert response.c.profile != None
        assert 'Rubicon Web Player' in response

    def test_get_data(self):

        # Test that failure is returned on bad invocation
        response = self.app.get(url_for(
            controller='player', 
            action='get_data'
        ))
        assert '"success": false' in response

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
            response = self.app.get(url_for(
                controller='player', 
                action='get_data'
            ), params={'type': type })
            assert '"success": true' in response

    def test_get_url(self):
        response = self.app.get(url_for(
            controller='player',
            action = 'get_song_url',
            id = 44
        ))

        assert response.session.has_key('playing') == True,\
            "file being played not inserted into session as expected"
        assert 'music.rubiconmusicplayer.com' in response

        # Now we'll mark a particular file as completely consumed (should die)
        files=model.Session.query(model.File).\
            filter(model.File.songid == 45).all()
        not_friend = model.Sesssion.query(User).\
            filter(User.fbid == 1906978).first()
        for file in files:
            pylons.g.usedfiles[(file.id, file.ownerid)] = file.owners

        response = self.app.get(url_for(
            controller='player',
            action = 'get_song_url',
            id = 45
        ))
        assert response.status == 404, \
            "file was found when it should not have been"
