from masterapp.tests import *
#from masterapp import model

class TestPlayerController(TestController):
    def test_index(self):
        """
        Testing <root>/player
        """
        response = self.app.get(
            url_for(controller='player'), headers = self.dheaders)
        # Test response...
        assert response.c.profile != None
        assert 'player | harmonize.fm' in response

    def test_get_song_url(self):
        """
        Testing <root>/player/songurl/<songid>
        """
        response = self.app.get(url_for(
            controller='player',
            action = 'songurl',
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
            action = 'songurl',
            id = 8
        ))
        assert 'false' in response, \
            "file was found when it should not have been"
