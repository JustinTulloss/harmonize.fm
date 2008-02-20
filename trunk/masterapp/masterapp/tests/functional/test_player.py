from masterapp.tests import *

class TestPlayerController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='player'))
        # Test response...
        assert response.c.profile != None

    def test_get_data(self):
        response = self.app.get(url_for(
            controller='player', 
            action='get_data'
        ))
