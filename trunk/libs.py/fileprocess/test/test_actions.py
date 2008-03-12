import unittest
import logging
import nose
from nose.tools import *
from mockfiles import mockfiles
from ..actions.mover import Mover
from ..actions.taggetter import TagGetter
from ..actions.brainztagger import BrainzTagger

import os, shutil
from pylons import config
from paste.deploy import appconfig

class TestActions(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        config.update(
            appconfig( 'config://'+os.path.abspath(os.curdir)+\
                '/../../masterapp/development.ini'
            )
        )
        config['upload_dir']='./test/testuploaddir'
        config['media_dir']='./test/teststagingdir'
        os.mkdir(config['media_dir'])
        shutil.copytree('./test/testfiles', config['upload_dir'])

        self.fdata = mockfiles.copy()
        for key,f in mockfiles.iteritems():
            self.fdata[key]=f.copy()

    def tearDown(self):
        shutil.rmtree(config['upload_dir'])
        shutil.rmtree(config['media_dir'])

    def testMover(self):
        m = Mover()
        assert m is not None, "Mover not constructed"
        assert_raises(Exception, m.process, self.fdata['empty'])
        assert_false(m.process(self.fdata['neupload']),
            "Did not remove nonexistent file from queue")
        outfile = m.process(self.fdata['goodfile'])
        assert 'teststaging' in outfile['fname']
    
    def testTagger(self):
        t = TagGetter()
        assert t is not None, "Tagger not constructed"
        assert_raises(Exception, t.process, self.fdata['empty'])
        assert_raises(Exception, t.process,self.fdata['neupload'])

        self.fdata['notmp3']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['notmp3']['fname'])
        assert_false(t.process(self.fdata['notmp3']))

        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        nf = t.process(self.fdata['goodfile'])
        assert nf.has_key('title'), "Did not tag title"
        assert nf['title'] == u'Happiness Is a Warm Gun', "Title is incorrect"
        assert nf.has_key('album'), "Did not tag album"
        assert nf.has_key('artist'), "Did not tag artist"
    
    def testBrainz(self):
        b = BrainzTagger()
        assert b is not None, "BrainzTagger not constructed"

        of = self.fdata['nonexistenttags'].copy()
        nf = b.process(self.fdata['nonexistenttags'])
        assert of == nf, 'Brainz modified a file without a match'

        nf = b.process(self.fdata['goodtags'])
        assert nf, "Brainz failed to process properly tagged song"
        assert nf.has_key('asin'), "Brainz did not fill in new tags"

        nf = b.process(self.fdata['badtags'])
        assert nf, "Brainz failed to process badly tagged song"
        assert nf['artist'] == u"Office", "Brainz did not correct artist"
        assert u"Ritz" in nf['album'], "Brainz did not correct album"
        assert b.artistcache != {}, "Brainz did not cache artist"
        assert b.albumcache != {}, "Brainz did not cache album"

        nf = b.process(self.fdata['incompletetags'])
        assert u'Broken Bride' in nf['album'], \
            "Brainz did not fill in missing album"

        assert_false(b.process(self.fdata['multipleversions']))
