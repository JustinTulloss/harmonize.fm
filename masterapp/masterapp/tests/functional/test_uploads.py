import os, shutil
import socket
from masterapp.tests import *
from nose.tools import assert_raises
from paste.fixture import AppError
from masterapp.controllers.upload import Response
from pylons import config

class TestUploadController(TestModel):
    def __init__(self, *args, **kwargs):
        super(TestUploadController, self).__init__(*args, **kwargs)

    def test_tags(self):
        """
        Testing <root>/upload/tags
        """
        res = self.app.get('/upload/tags')
        assert res.body == 'reauthenticate'

        debra = dict(
            session_key = config['pyfacebook.sessionkey'],
            puid = '1a375417-16a7-4d26-80c1-b8500253b28a',
            artist = 'Beck',
            album = 'Midnite Vultures',
            title = 'Debra',
            duration = 338892.289,
            date = 1999,
            genre = 'Rock'
        )

        generate_fake_user(config['pyfacebook.fbid'])

        # Test malformed request
        self.app.post('/upload/tags', params=debra, status=400)

        debra['version'] = '1.0' # Make the request legit

        #self._listen()
        # A test of a file we haven't seen before
        res = self.app.post('/upload/tags', params=debra)
        assert res.body == Response.upload

        # Put a file in the database that has the same mbid but different puid
        nsong = model.Song(
            title = 'Debra',
            mbid = '8f2ac91a-da7c-4ad5-8ee3-078c444053bf'
        )
        nsong.album = model.Album(title = 'Midnite Vultures')
        nsong.artist = model.Artist(name = 'Beck')
        npuid = model.Puid(puid = 'ea67e6dc-7928-7965-ab3b-16fcbd6e287a')
        npuid.song = nsong
        model.Session.add(nsong.album)
        model.Session.add(nsong.artist)
        model.Session.add(nsong)
        model.Session.add(npuid)
        model.Session.commit()

        # Test to make sure the song we just put in the db is found
        res = self.app.post('/upload/tags', params=debra)
        assert res.body == Response.done

        # Test a song with the same tags
        debra['puid'] = None
        res = self.app.post('/upload/tags', params = debra)
        assert res.body == Response.done
        #self._stop_listening()

    def test_file(self):
        """
        Testing <root>/upload/file
        """
        res = self.app.post(
            '/upload/file/23620cde3a549a043a20d1e9c2b4c1c85899d2f9'
        )
        assert res.body == 'reauthenticate'

        user = generate_fake_user(config['pyfacebook.fbid'])

        testfilepath = os.path.join(here_dir, 'functional', '02 Vacileo.mp3')
        testfile = open(testfilepath)
        size = os.stat(testfilepath)[os.path.stat.ST_SIZE]
        url ='/upload/file/23620cde3a549a043a20d1e9c2b4c1c85899d2f9'+\
            '?session_key=%s' % config['pyfacebook.sessionkey']

        self._listen()
        res = self.app.post(url,
            params = testfile.read(),
            headers = {
                'content-length': str(size),
                'content-type': 'audio/x-mpeg-3'
            }
        )
        assert res.body == Response.done, "File not properly uploaded"

        assert os.path.exists(
            os.path.join(conf_dir,'tmp','1909354',
                '23620cde3a549a043a20d1e9c2b4c1c85899d2f9'
            )), 'Uploaded file does not exist'

        # Cleanup file
        shutil.rmtree(os.path.join(conf_dir, 'tmp', '1909354'))
        self._stop_listening()

    def _listen(self):
        # Hook up to socket uploader will send file down
        self.fsock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        port = int(config['pipeline_port'])
        self.fsock.bind(('localhost', port))
        self.fsock.listen(10)

    def _stop_listening(self):
        self.fsock.close()

