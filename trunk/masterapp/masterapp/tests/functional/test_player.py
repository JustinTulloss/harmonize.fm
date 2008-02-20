from masterapp.tests import *

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
