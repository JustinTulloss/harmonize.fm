import os
from masterapp.tests import *

class TestUploadsController(TestController):
    def test_upload_new(self):
        """
        Testing <root>/uploads/id
        """
        res = self.app.get('/uploads/')
        assert res.body == 'reauthenticate'

        # Read a valid fingerprint for an average test
        fd = open(os.path.join(here_dir, 'functional', 'fingerprint'))
        fp = fd.read().strip()

        debra = dict(
            version = '1.0',
            session_key = '08bd66d3ebc459d32391d0d2-1909354',
            fingerprint = fp,
            artist = 'Beck',
            album = 'Midnite Vultures',
            title = 'Debra',
            duration = 338892.289,
            date = 1999,
            genre = 'Rock'
        )

        # A test of a file we haven't seen before
        res = self.app.post('/uploads/fingerprint', params=debra)
        print res.body
