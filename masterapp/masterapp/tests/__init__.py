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
from pylons import config,cache

__all__ = ['url_for', 'TestController', 'TestModel', 'here_dir',
    'conf_dir', 'model']

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
config['pylons.g'].sa_engine = reflectengine
memengine = engine_from_config(config,
    prefix = 'sqlalchemy.memory.')

from masterapp import model

# Bind to memory database and create all
config['pylons.g'].sa_engine = memengine
model.metadata.bind = memengine
model.Session.bind=memengine
model.metadata.create_all()

test_file = os.path.join(conf_dir, 'test.ini')
cmd = paste.script.appinstall.SetupCommand('setup-app')
cmd.run([test_file])

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        #wsgiapp = PylonsApp(config='config:test.ini', base_wsgi_app=wsgiapp)
        self.app = paste.fixture.TestApp(wsgiapp)
        super(TestController, self).__init__(*args, **kwargs)

        self.dheaders = {
            'USER_AGENT': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9) Gecko/2008052912 Firefox/3.0'
        }

class TestModel(TestController):
    def __init__(self, *args):
        super(TestModel, self).__init__(*args)

    def setUp(self):
        super(TestModel, self).setUp()
        model.metadata.create_all()

    def tearDown(self):
        super(TestModel, self).tearDown()
        model.metadata.drop_all()
        model.Session.remove()

        #self.model.Session.configure(bind=reflectengine)
        #self.model.metadata.bind = reflectengine

