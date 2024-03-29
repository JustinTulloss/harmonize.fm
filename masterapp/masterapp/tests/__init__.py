"""Pylons application test package

When the test runner finds and executes tests within this directory,
this file will be loaded to setup the test environment.

It registers the root directory of the project in sys.path and
pkg_resources, in case the project hasn't been installed with
setuptools. It also initializes the application via websetup (paster
setup-app) with the project's test.ini configuration file.
"""
import os
import sys
import hashlib
from unittest import TestCase

import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
from routes import url_for

from sqlalchemy import engine_from_config
from sqlalchemy import engine
from pylons import config

__all__ = ['url_for', 'TestController', 'TestModel', 'here_dir',
    'conf_dir', 'model', 'generate_fake_song', 'generate_fake_user',
    'generate_fake_playlist']

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)
pkg_resources.working_set.add_entry(conf_dir)
pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)

# Set up reflect engine to autload metadata from dev database
reflectengine = engine_from_config(config,
    prefix = 'sqlalchemy.default.'
)
memengine = engine_from_config(config,
    prefix = 'sqlalchemy.memory.')

config['pylons.g'].sa_engine = reflectengine
from masterapp import model

# Bind to memory database and create all
config['pylons.g'].sa_engine = memengine
model.metadata.bind = memengine
model.Session.configure(bind = memengine)
model.metadata.create_all()

test_file = os.path.join(conf_dir, 'test.ini')
cmd = paste.script.appinstall.SetupCommand('setup-app')
cmd.run([test_file])

from masterapp.lib import fbauth



class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        #wsgiapp = PylonsApp(config='config:test.ini', base_wsgi_app=wsgiapp)
        #setup app with proxies made availables
        self.app = paste.fixture.TestApp(wsgiapp)

        """
        I got the stuff below from pylons.commands
        It solves lots of our SOP problems and I wish I didn't have to go
        digging for this stuff myself
        """
        # Query the test app to setup the environment
        tresponse = self.app.get('/_test_vars')
        request_id = int(tresponse.body)

        # Disable restoration during test_app requests
        self.app.pre_request_hook = lambda self: \
            paste.registry.restorer.restoration_end()
        self.app.post_request_hook = lambda self: \
            paste.registry.restorer.restoration_begin(request_id)

        self.request_id = request_id


        super(TestController, self).__init__(*args, **kwargs)

        self.linux_ff3_headers = {
            'USER_AGENT': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9) Gecko/2008052912 Firefox/3.0'
        }

        self.mac_ff3_headers = {
            'USER_AGENT': "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9) Gecko/2008061004 Firefox/3.0"
        }

        self.mac_safari3_headers = {
            'USER_AGENT': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_3; en-us) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.1 Safari/525.20'
        }

        self.win_ff2_headers = {
            'USER_AGENT':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.15) Gecko/20080623 Firefox/2.0.0.15'
        }
        self.win_ie6_headers = {
            'USER_AGENT': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; IBP; .NET CLR 1.1.4322)"
        }
    def setUp(self):
        # Restore the state of the Pylons special objects
        # (StackedObjectProxies)
        paste.registry.restorer.restoration_begin(self.request_id)

    def tearDown(self):
        # Nuke the caches
        from pylons import cache
        try:
            for c in cache.caches.itervalues():
                c.clear()
            cache.caches.clear()
        except TypeError, e:
            print "Couldn't clear the caches"
        paste.registry.restorer.restoration_end()

class TestModel(TestController):
    def __init__(self, *args):
        super(TestModel, self).__init__(*args)
        model.metadata.bind = memengine
        model.Session.configure(bind=memengine)

    def setUp(self):
        super(TestModel, self).setUp()
        model.Session.remove()
        model.Session()
        model.metadata.create_all()
        self.user = generate_fake_user(config['pyfacebook.fbid'])

    def tearDown(self):
        super(TestModel, self).tearDown()
        model.metadata.drop_all()

rnum = 0
def generate_fake_song(owner):
        global rnum
        rnum +=1
        rstr = str(rnum)
        nal = model.Album(title = 'album'+rstr)
        nar = model.Artist(name = 'artist'+rstr)
        nal.artist = nar
        ns = model.Song(title="A song"+rstr, sha = 'sha'+rstr)
        ns.artist = nar
        ns.album = nal

        owner.add_song(ns)

        model.Session.add_all([owner, nal, nar, ns])
        model.Session.commit()
        return ns

def generate_fake_playlist(owner, songs=1):
    global rnum
    rnum += 1
    rstr = str(rnum)
    playlist = model.Playlist('Playlist'+rstr, owner.id)
    model.Session.add(playlist)
    for i in range(songs):
        song=generate_fake_song(owner)
        plsong = model.PlaylistSong(playlist.id, i, song.id)
        playlist.songs.append(plsong)
    model.Session.commit()
    return playlist

def generate_fake_user(fbid=None):
    global rnum
    rnum += 1
    rstr = str(rnum)
    user = fbauth.create_user(fbid = fbid if fbid else 'id'+rstr)
    model.Session.commit()
    return user
    
