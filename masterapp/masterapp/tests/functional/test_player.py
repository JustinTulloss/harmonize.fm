from masterapp.tests import *
import re
from mock import Mock
#from masterapp import model

class TestPlayerController(TestModel):
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
        # Test 404 for a non-existent song
        response = self.app.get(url_for(
            controller='player',
            action = 'songurl',
            id = 7
        ), status=404)


        # Test for a song I do own
        ns = generate_fake_song(model.Session.query(model.User).one())
        response = self.app.get(url_for(
            controller='player',
            action = 'songurl',
            id = ns.id
        ))

        assert re.search(ns.sha, response.body),\
            'Did not return the sha in the URL'
        
        # Test for a song none of my friends own
        anewuser = generate_fake_user()
        anewsong = generate_fake_song(anewuser)

        response = self.app.get(url_for(
            controller='player',
            action = 'songurl',
            id = anewsong.id
        ), params={'friend': anewuser.id}, status=401)
