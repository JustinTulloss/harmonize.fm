from masterapp.tests import *

class TestPlayerController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='player'))
        # Test response...