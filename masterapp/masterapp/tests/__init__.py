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
#from masterapp import model
#from masterapp.lib import populate_model

__all__ = ['url_for', 'TestController', 'TestModel']

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)
pkg_resources.working_set.add_entry(conf_dir)
pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

test_file = os.path.join(conf_dir, 'test.ini')
#cmd = paste.script.appinstall.SetupCommand('setup-app')
#cmd.run([test_file])

#Populate test data here. Remember to undo any changes you make to the data.
#model.metadata.create_all(model.Session.bind)
#populate_model.populate()
#config['pylons.g'] 
class TestModel(TestCase):
    def __init__(self, *args):
        super(TestModel, self).__init__(*args)

        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        reflectengine = engine_from_config(config,
            prefix = 'sqlalchemy.reflect.'
        )
        config['pylons.g'].sa_engine = reflectengine
        memengine = engine_from_config(config,
            prefix = 'sqlalchemy.default.')
        from masterapp import model
        self.model = model

        self.app = paste.fixture.TestApp(wsgiapp)

    def setUp(self):
        super(TestModel, self).setUp()
        self.model.metadata.bind = memengine
        self.model.Session.configure(bind=memengine)
        self.model.Session.remove()
        self.model.metadata.create_all()

    def tearDown(self):
        super(TestModel, self).tearDown()
        self.model.metadata.drop_all()

        self.model.Session.configure(bind=reflectengine)
        self.model.metadata.bind = reflectengine

class TestController(TestModel):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
