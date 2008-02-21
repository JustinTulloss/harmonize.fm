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
from unittest import TestCase

import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
from routes import url_for

from sqlalchemy import engine_from_config
from masterapp import model

__all__ = ['url_for', 'TestController', 'TestModel', 'model']

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)
pkg_resources.working_set.add_entry(conf_dir)
pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

test_file = os.path.join(conf_dir, 'test.ini')
cmd = paste.script.appinstall.SetupCommand('setup-app')
cmd.run([test_file])

"""
Fake Data. Sorry, I really don't care to put this elsewhere
"""
mockfbids = {'brian':1908861,'justin':1909354, 'alex':1906752, 'beth':1906978}

class TestModel(TestCase):
    def setUp(self):
        model.Session.remove()
        model.metadata.create_all(model.Session.bind)
        self.populate_model()

    def tearDown(self):
        model.metadata.drop_all(model.Session.bind)

    def populate_model(self):
        for fbid in mockfbids.itervalues():
            user = model.User(fbid)
            model.Session.save(user)

        model.Session.commit()


class TestController(TestModel):

    def __init__(self, *args, **kwargs):
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
        TestCase.__init__(self, *args, **kwargs)
