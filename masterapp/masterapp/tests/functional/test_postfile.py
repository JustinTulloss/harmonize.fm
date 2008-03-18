from masterapp.tests import *

class TestPostfileController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='postfile'))
        # Test response...