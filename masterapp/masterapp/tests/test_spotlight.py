from masterapp.tests import *
from nose.tools import assert_raises
from paste.fixture import AppError
from pylons import config
from mock import Mock, patch
from facebook.wsgi import facebook

class TestSpotlightController(TestModel):

    def __init__(self, *args, **kwargs):
        super(TestSpotlightController, self).__init__(*args, **kwargs)

    def test_album(self):
        """
        Testing /spotlight/album/<albumid>
        """
        # bad request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'album'
        ), params={'comment': 'Commenting on a bad spotlight'}, status=400)


        # Average request
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'album',
            id = song.albumid
        ), params={'comment': 'Commenting on a spotlight'})
        assert response.body == '1', 'Spotlight not created successfully'
        #assert facebook.feed.publishTemplatizedAction.called, 'Feed not updated'
        #assert facebook.profile.setFBML.called, 'Profile fbml not updated'
        assert model.Session.query(model.Spotlight).all(),\
            "Spotlight not in database"
        assert len(self.user.spotlights) >0, \
            "Spotlight not associated with user"

    def test_playlist(self):
        """
        Testing /spotlight/playlist/<playlistid>
        """
        # bad request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'playlist',
            id = None
        ), params={'comment': 'Commenting on a bad spotlight'}, status=400)

        # test a non-existent playlist
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'playlist',
            id = 1
        ), params={'comment': 'Commenting on a phantom playlist'}, status=404)

        # Average request
        song = generate_fake_song(self.user)
        playlist = model.Playlist('Playing', self.user.id)
        model.Session.add(playlist)
        model.Session.commit()

        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'playlist',
            id = playlist.id
        ), params={'comment': 'Commenting on a spotlight'})
        assert response.body == '1', 'Spotlight not created successfully'
        #assert facebook.feed.publishTemplatizedAction.called, 'Feed not updated'
        #assert facebook.profile.setFBML.called, 'Profile fbml not updated'
        assert model.Session.query(model.Spotlight).all()
        assert model.Session.query(model.Spotlight).all(),\
            "Spotlight not in database"
        assert len(self.user.spotlights) >0, \
            "Spotlight not associated with user"

