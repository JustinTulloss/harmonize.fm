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
        rec = model.Session.query(model.Recommendation).one()
        assert rec.recommenderid == self.user.id, \
            'Did not put user as recommender in the database'
        assert rec.recommendeefbid == friends[0], \
            'Did not put user as recommendee in the database'
        assert rec.albumid and not rec.playlistid and not rec.songid, \
            'Did not set the correct recommendation values'

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
        rec = model.Session.query(model.Recommendation).one()
        assert rec.recommenderid == self.user.id, \
            'Did not put user as recommender in the database'
        assert rec.recommendeefbid == friends[0], \
            'Did not put user as recommendee in the database'
        assert rec.songid and not rec.playlistid and not rec.albumid, \
            'Did not set the correct recommendation values'

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
        rec = model.Session.query(model.Recommendation).one()
        assert rec.recommenderid == self.user.id, \
            'Did not put user as recommender in the database'
        assert rec.recommendeefbid == friends[0], \
            'Did not put user as recommendee in the database'
        assert rec.playlistid and not rec.songid and not rec.albumid, \
            'Did not set the correct recommendation values'
