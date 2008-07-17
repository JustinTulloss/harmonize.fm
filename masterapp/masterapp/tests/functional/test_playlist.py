from masterapp.tests import *
from masterapp.lib.fakefacebook import friends, friends_info
import simplejson

class TestPlaylistController(TestModel):
    def test_create(self):
        """
        Testing /playlist/create
        """
        # Not passing in the required parameters
        response = self.app.get(url_for(
            controller='playlist',
            action='create'
        ), status = 400)

        name = 'test playlist'
        response = self.app.get(url_for(
            controller='playlist',
            action='create'
        ), params = {'name': name})
        data = simplejson.loads(response.body)['data']
        assert data[0]['Playlist_name'] == name, \
            'Did not create playlist with correct name'

    def test_delete(self):
        """
        Testing /playlist/delete/:id
        """
        playlist = generate_fake_playlist(self.user)
        playlist_id = playlist.id
        response = self.app.get(url_for(
            controller='playlist',
            action='delete',
            id=str(playlist_id)
        ))
        assert model.Session.query(model.Playlist).get(playlist_id) == None,\
                'Playlist did not get deleted'

        #Make sure we can't delete a friend's playlist
        friend = generate_fake_user(friends[0])
        playlist = generate_fake_playlist(friend)
        response = self.app.get(url_for(
            controller='playlist',
            action='delete',
            id=playlist.id
        ), status=404)
    
    def test_save(self):
        """
        Testing /playlist/save
        """

        #Try saving to a non-existent playlist
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller='playlist',
            action='save'
        ), params={'playlist': '1', 'songs': int(song.id)}, status=400)

        #A possibly valid song to save
        playlist = generate_fake_playlist(self.user)
        response = self.app.get(url_for(
            controller='playlist',
            action='save'
        ), params={'playlist': str(playlist.id), 'songs': '1234'},
           status=404)

        '''
        song2 = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller='playlist',
            action='save'
        ), params={'playlist': str(playlist.id), 
                    'songs': str(song.id)+','+str(song2.id)})
        playlist2 = model.Session.query(model.Playlist).get(playlist.id)
        assert response.body == '1', 'Save was not successful'
        assert len(playlist2.songs) == 2, 'Not all songs saved'
        songs = (playlist2.songs[0].id, playlist2.songs[1].id)
        assert song.id in songs and song2.id in songs,\
                'Playlist did not contain the correct songs'

        #Try and save friends music to the playlist
        friend_playlist = generate_fake_playlist(friends[0])
        response = self.app.get(url_for(
            controller='playlist',
            action='save'
        ), params={'playlist': str(friend_playlist.id),
                    'songs': str(song.id)}, response=404)
        '''
