import unittest
import nose
from nose.tools import *
from mockfiles import mockfiles
from ..actions.mover import Mover
from ..actions.taggetter import TagGetter

import os, shutil
from pylons import config
from paste.deploy import appconfig

class TestActions(unittest.TestCase):
    def setUp(self):
        config.update(
            appconfig( 'config://'+os.path.abspath(os.curdir)+\
                '/../../masterapp/development.ini'
            )
        )
        config['upload_dir']='./test/testuploaddir'
        config['media_dir']='./test/teststagingdir'
        os.mkdir(config['media_dir'])
        shutil.copytree('./test/testfiles', config['upload_dir'])
        self.fdata = dict(mockfiles)

    def tearDown(self):
        shutil.rmtree(config['upload_dir'])
        shutil.rmtree(config['media_dir'])
        self.fdata = None

    def testMover(self):
        m = Mover()
        assert m is not None, "Mover not constructed"
        self.check_baseline(m)
        assert_false(m.process(self.fdata['neupload']),
            "Did not remove nonexistent file from queue")
        outfile = m.process(self.fdata['goodfile'])
        assert 'teststaging' in outfile['fname']
    
    def testTagger(self):
        t = TagGetter()
        assert t is not None, "Tagger not constructed"
        self.check_baseline(t)
        assert_raises(Exception, t.process,self.fdata['neupload'])

        t.process(self.fdata['goodfile'])

    def check_baseline(self, o):
        assert_raises(Exception, o.process, self.fdata['empty'])

