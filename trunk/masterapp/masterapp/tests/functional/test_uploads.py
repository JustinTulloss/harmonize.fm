from masterapp.tests import *

class TestUploadsController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='uploads'))
        # Test response...
