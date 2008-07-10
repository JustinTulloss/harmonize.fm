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
        assert response.body != '0', 'Spotlight not created successfully'
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

    def test_edit(self):
        """
        Testing /spotlight/edit/<spotlightid>
        """
        # Test malformed request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'edit',
            id = None
        ), status=400)

        song = generate_fake_song(self.user)
        # Create an album spotlight to edit
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'album',
            id = song.albumid,
        ), params={'comment': 'A new spotlight'})
        id = int(response.body)

        # Edit that spotlight
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'edit',
            id = id
        ), params={'comment': 'A modified spotlight'})

        assert response.body == '1', \
            "spotlight edit did not return true"
        sp = model.Session.query(model.Spotlight).get(id)
        assert sp.comment == 'A modified spotlight',\
            "Spotlight comment was not changed"

    def test_delete(self):
        """
        Testing /spotlight/delete/<spotlightid>
        """
        # Test malformed request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'delete',
            id = None
        ), status = 400)

        # create a spotlight to delete
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'album',
            id = song.albumid,
        ), params={'comment': 'A new spotlight'})
        id = int(response.body)

        # Delete a spotlight
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'delete',
            id = id
        ))
        assert response.body == '1',\
            "Deleting spotlight did not return success"
        assert not model.Session.query(model.Spotlight).all(),\
            "Spotlight not deleted"

        # create a playlist spotlight to delete
        playlist = model.Playlist("PL", self.user.id)
        model.Session.add(playlist)
        model.Session.commit()
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'playlist',
            id = playlist.id
        ), params={'comment': 'Spotlightin the old list'})
        id = int(response.body)

        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'delete',
            id = playlist.id
        ))

        assert response.body == '1', \
            "delete spotlight did not return success"
        assert not model.Session.query(model.Spotlight).all(),\
            "Spotlight not deleted"

    def test_find_album(self):
        """
        Testing /spotlight/find_album/<spotlightid>
        """
        # Test illegit request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_album',
            id = None
        ), status = 400)
        
        # Create a spotlight
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'album',
            id = song.albumid
        ), params={'comment': 'Making a spotlight'})
        id = str(response.body)

        # Fetch that spotlight
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_album',
            id = id
        ))
        assert '"Spotlight_id": %s' % id in response.body,\
            "Did not return created spotlight"

    def test_find_playlist(self):
        """
        Testing /spotlight/find_playlist/<spotlightid>
        """
        # Test illegit request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_playlist',
            id = None
        ), status = 400)
        
        # Create a spotlight
        playlist = generate_fake_playlist(self.user)
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'playlist',
            id = playlist.id
        ), params={'comment': 'Making a spotlight'})
        id = str(response.body)

        # Fetch that spotlight
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_playlist',
            id = id
        ))
        assert '"Spotlight_id": %s' % id in response.body,\
            "Did not return created spotlight"

    def find_by_album(self, id):
        """
        Testing /spotlight/find_by_album/<albumid>
        """
        # Test illegit request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_by_album',
            id = None
        ), status = 400)
        
        # Create a spotlight
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'album',
            id = song.albumid
        ), params={'comment': 'Making a spotlight'})
        id = str(response.body)

        # Fetch that spotlight
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_by_album',
            id = song.albumid
        ))
        assert responze.body == '1',\
            "Did not return created spotlight"

    def find_by_playlist(self, id):
        """
        Testing /spotlight/find_by_playlist/<playlistid>
        """
        # Test illegit request
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_by_playlist',
            id = None
        ), status = 400)
        
        # Create a spotlight
        playlist = generate_fake_playlist(self.user)
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'playlist',
            id = playlist.id
        ), params={'comment': 'Making a spotlight'})
        id = str(response.body)

        # Fetch that spotlight
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'find_by_playlist',
            id = playlist.id
        ))
        assert response.body == '1',\
            "Did not find spotlight"
        
        
