import unittest
import logging
import nose
from nose.tools import *
from mockfiles import mockfiles
from ..actions import Mover, TagGetter, BrainzTagger, Cleanup, FacebookAction,\
    S3Uploader
import fileprocess

import pymock
import os, shutil, sys
sys.path.append('..')
from mock import Mock, patch, sentinel

from pylons import config
from paste.deploy import appconfig

class TestActions(unittest.TestCase):
    def setUp(self):
        os.path
        logging.basicConfig(level=logging.INFO)
        config.update(
            appconfig( 'config://'+os.path.abspath(os.curdir)+\
                '/../../masterapp/test.ini'
            )
        )
        config['upload_dir']='./test/testuploaddir'
        config['media_dir']='./test/teststagingdir'
        os.mkdir(config['media_dir'])
        shutil.copytree('./test/testfiles', config['upload_dir'])


        self.fdata = mockfiles.copy()
        for key,f in mockfiles.iteritems():
            self.fdata[key]=f.copy()

            # Also add mocked session
            self.fdata[key]['session'] = Mock(spec={})
            self.fdata[key]['session']._methods.append('save')
            self.fdata[key]['session'].has_key.return_value=True
            self.fdata[key]['session'].get.return_value = []

    def tearDown(self):
        shutil.rmtree(config['upload_dir'])
        shutil.rmtree(config['media_dir'])

    def testMover(self):
        m = Mover()
        m.cleanup_handler = Mock()
        assert m is not None, "Mover not constructed"

        # Test empty file
        assert_raises(Exception, m.process, self.fdata['empty'])
        assert_false(m.process(self.fdata['neupload']),
            "Did not remove nonexistent file from queue")
        assert m.cleanup_handler.put.called, "Cleanup not called on empty file"
        m.cleanup_handler.reset()

        # Test good file
        outfile = m.process(self.fdata['goodfile'])
        assert 'teststaging' in outfile['fname']
    
    def testTagger(self):
        t = TagGetter()
        assert t is not None, "Tagger not constructed"

        # Test bad file dicts
        assert_raises(Exception, t.process, self.fdata['empty'])
        assert_raises(Exception, t.process,self.fdata['neupload'])

        # Test a clearly invalid file
        self.fdata['notmp3']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['notmp3']['fname'])
        assert_false(t.process(self.fdata['notmp3']))

        # Test a good file
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        nf = t.process(self.fdata['goodfile'])
        assert nf.has_key('title'), "Did not tag title"
        assert nf['title'] == u'Happiness Is a Warm Gun', "Title is incorrect"
        assert nf.has_key('album'), "Did not tag album"
        assert nf.has_key('artist'), "Did not tag artist"
    
    def testBrainz(self):
        b = BrainzTagger()
        b.cleanup_handler = Mock()
        assert b is not None, "BrainzTagger not constructed"

        # Test a song not in the brainz database
        of = self.fdata['nonexistenttags'].copy()
        assert_false(b.process(self.fdata['nonexistenttags']))
        assert b.cleanup_handler.put.called, \
            "Cleanup not called on nonexistent tags"
        b.cleanup_handler.reset()

        # Test a song that is a shoe in
        nf = b.process(self.fdata['goodtags'])
        assert nf, "Brainz failed to process properly tagged song"
        assert nf.has_key('asin'), "Brainz did not fill in new tags"

        # Test a song that is improperly tagged but should be corrected
        nf = b.process(self.fdata['badtags'])
        assert nf, "Brainz failed to process badly tagged song"
        assert nf['artist'] == u"Office", "Brainz did not correct artist"
        assert u"Ritz" in nf['album'], "Brainz did not correct album"
        assert b.artistcache != {}, "Brainz did not cache artist"
        assert b.albumcache != {}, "Brainz did not cache album"

        # Test a song that is incompletely tagged but should be found
        nf = b.process(self.fdata['incompletetags'])
        assert u'Broken Bride' in nf['album'], \
            "Brainz did not fill in missing album"

        # Test a song for which there are multiple brainz matches
        assert_false(b.process(self.fdata['multipleversions']))
        assert b.cleanup_handler.put.called, \
            "Cleanup not called on multipleversions"
        b.cleanup_handler.reset()

    def testCleanup(self):
        c = Cleanup()
        assert c is not None, "Cleanup not constructed"

        # Test file removal and saving the session
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        nf = c.process(self.fdata['goodfile'])
        assert self.fdata['goodfile']['session'].save.called, \
            "Cleanup did not update session"
        assert_false(os.path.exists(self.fdata['goodfile']['fname']),
            "Cleanup did not remove file")

    def testFacebook(self):
        f = FacebookAction()
        f.cleanup_handler = Mock()
        assert f is not None, "Facebook Action not constructed"
        
        # Test bad facebook session
        assert_false(f.process(self.fdata['badfbsession']))
        assert f.cleanup_handler.put.called,\
            "Did not properly cleanup after facebook failed"
        assert self.fdata['badfbsession']['na'] == fileprocess.na.AUTHENTICATE,\
            "Facebook Action did not request reauthentication"

        nf = f.process(self.fdata['goodfbsession'])
        assert nf['fbid'] is not None, \
            "Facebook Action failed to populate facebook uid"

    def testS3(self):
        s = S3Uploader()
        assert s is not None, "S3 uploader not constructed"
        s.cleanup_handler = Mock()

        config['S3.upload'] = True

        # Test an empty file
        assert_raises(AssertionError, s.process, self.fdata['empty'])

        # Test a nonexistent file
        # XXX: This doesn't actually make sense. If for some reason,
        # the file is lost, we need to undo everything we've done. It's
        # a bad situation that will hopefully never happen.
        assert_false(s.process(self.fdata['neupload']),
            "Did not fail on nonexistent file"
        )

        # Test a good file (patch out the actual upload)
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        putfxn = Mock()
        putfxn.return_value = sentinel
        putfxn.return_value.message = '200 OK'
        import S3
        @patch(S3.AWSAuthConnection, 'put', putfxn)
        def upload(file):
            s.process(file)

        upload(self.fdata['goodfile'])
        assert putfxn.called, "S3 did not upload file"
        assert s.cleanup_handler.put.called, \
            "S3 did not clean up local file"
        s.cleanup_handler.put.reset()

        # Test for when S3 returns an error
        putfxn.return_value.message = '500 Server Error'
        upload(self.fdata['goodfile'])
        assert s.cleanup_handler.put.called, \
            "S3 did not clean up local file"
        s.cleanup_handler.put.reset()

        
        # Test the development no-op code
        config['S3.upload'] = False
        nf = s.process(self.fdata['goodfile'])
        assert s.cleanup_handler.put.called, \
            "S3 did not clean up local file when not uploading"

