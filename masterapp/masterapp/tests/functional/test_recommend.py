from masterapp.tests import *
from masterapp.lib.fakefacebook import friends
#from masterapp import model

class TestRecommendController(TestModel):
    
    def test_album(self):
        """
        Testing /recommend/album/<albumid>/<friendid>
        """
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'recommend',
            action = 'album',
            entity = song.albumid,
            friend = friends[0]
        ))
        c = response.request.environ['paste.testing_variables']['c'] 
        assert response.body == '1',\
            "Did not return success"
        assert c.recommender == self.user,\
            "Did not put user as recommender"

    def test_artist(self):
        """
        Testing /recommend/artist/<artistid>/<friendid>
        """
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'recommend',
            action = 'artist',
            entity = song.artistid,
            friend = friends[0]
        ))
        c = response.request.environ['paste.testing_variables']['c'] 
        assert response.body == '1',\
            "Did not return success"
        assert c.recommender == self.user,\
            "Did not put me as recommender"

    def test_song(self):
        """
        Testing /recommend/song/<songid>/<friendid>
        """
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'recommend',
            action = 'song',
            entity = song.id,
            friend = friends[0]
        ))
        c = response.request.environ['paste.testing_variables']['c'] 
        assert response.body == '1',\
            "Did not return success"
        assert c.recommender == self.user,\
            "Did not put me as recommender"

    def test_playlist(self):
        """
        Testing /recommend/playlist/<playlistid>/<friendid>
        """
        playlist = generate_fake_playlist(self.user)
        response = self.app.get(url_for(
            controller = 'recommend',
            action = 'playlist',
            entity = playlist.id,
            friend = friends[0]
        ))
        c = response.request.environ['paste.testing_variables']['c'] 
        assert response.body == '1',\
            "Did not return success"
        assert c.recommender == self.user,\
            "Did not put me as recommender"
