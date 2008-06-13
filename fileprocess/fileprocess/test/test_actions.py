# -*- coding: utf8 -*-
# vim:expandtab:smarttab
import unittest
import logging
import nose
from nose.tools import *
from mockfiles import mockfiles
from ..actions import (Mover, TagGetter, BrainzTagger, Cleanup, FacebookAction,
    S3Uploader, DBChecker, DBRecorder, AmazonCovers, Hasher, Transcoder,
    PuidGenerator, DBTagger)
import fileprocess
from fileprocess.processingthread import na

from sqlalchemy import engine_from_config
from sqlalchemy import engine

from pylons import config as pconfig

import os, shutil, sys
from mock import Mock, patch, sentinel

from fileprocess.configuration import config, dev_config, test_config

class TestBase(unittest.TestCase):
    def __init__(self, *args):
        super(TestBase, self).__init__(*args)
        logging.basicConfig(level=logging.WARN)
        config.update(dev_config)
        config.update(test_config)

    def setUp(self):
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

class TestActions(TestBase):

    def testMover(self):
        m = Mover()
        m.cleanup_handler = Mock()
        assert m is not None, "Mover not constructed"

        # Test file that should be there but isn't
        assert_false(m.process(self.fdata['neupload']),
            "Did not remove nonexistent file from queue")
        assert m.cleanup_handler.queue.put.called, "Cleanup not called on empty file"
        m.cleanup_handler.reset()

        # Test good file
        outfile = m.process(self.fdata['goodfile'])
        assert 'teststaging' in outfile['fname']
    
    def testTagger(self):
        t = TagGetter()
        assert t is not None, "Tagger not constructed"

        # Test bad file dicts
        assert_raises(Exception, t.process, self.fdata['empty'])

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
        assert nf['filetype'] == 'mp3'

        # Test an mp4 file
        self.fdata['goodmp4']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodmp4']['fname'])
        nf = t.process(self.fdata['goodmp4'])
        assert nf.has_key('title'), "Did not tag title"
        assert nf['title'] == u'The Bandit', "Title is incorrect"
        assert nf.has_key('album'), "Did not tag album"
        assert nf.has_key('artist'), "Did not tag artist"
        assert nf['filetype'] == 'mp4'
    
    def testBrainz(self):
        b = BrainzTagger()
        b.cleanup_handler = Mock()
        assert b is not None, "BrainzTagger not constructed"

        # Test a song not in the brainz database
        of = self.fdata['nonexistenttags'].copy()
        nf = b.process(self.fdata['nonexistenttags'])
        assert nf['title'] == 'non-existent'

        # Test a song that is a shoo-in
        nf = b.process(self.fdata['goodtags'])
        assert nf, "Brainz failed to process properly tagged song"
        assert nf.has_key('asin'), "Brainz did not fill in new tags"
        assert nf['album'] == u'Crash', "Brainz messed up the correct tags"

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
        nf = b.process(self.fdata['multipleversions'])
        assert nf.has_key('album'),\
            "Brainz did not decide on a tag for multiversioned song"
        assert nf['totaltracks'] == 12, \
            'BrainzTagger didn\'t pick the right album'

        # Test a broken response from musicbrainz (which happens a lot)
        import musicbrainz2.webservice
        def getTracks(*args, **kwargs):
            raise musicbrainz2.webservice.WebServiceError("Testing Error")

        @patch(musicbrainz2.webservice.Query, 'getTracks', getTracks)
        @patch(musicbrainz2.webservice.Query, 'getReleases', getTracks)
        def query(file):
            b.releasecache = {}
            b.process(file)

        assert_false(query(self.fdata['goodtags']))
        assert b.cleanup_handler.queue.put.called, \
            "Cleanup not called on web service error"
        b.cleanup_handler.reset()

        # Test a tricky album to make sure our technique doesn't suck
        nf = b.process(self.fdata['amnesiac'])
        assert nf['album'] == 'Amnesiac', \
            "Album was "+nf['album'] + " instead of Amnesiac"

        # Now all the corner case tests. These are things that I've tweaked the
        # values specifically so that they are tagged correctly. They're put in
        # here so that future tweaking doesn't break them.

        # Bad title, good everything else
        b.releasecache = {}
        nf = b.process(self.fdata['abird'])
        assert nf['title'] == u'[image]', "Messed up Andrew Bird tagging"

        # Messes up the releasecache by being on a different album from tags
        b.releasecache = {}
        nf = b.process(self.fdata['btles2'])
        assert nf['album'] == u'The Beatles (disc 2)', "Cry baby not on disc 2"

        nf = b.process(self.fdata['btles1'])
        assert nf['album'] == u'The Beatles (disc 1)', "USSR not on disc 1"

    def testCleanup(self):
        c = Cleanup()
        assert c is not None, "Cleanup not constructed"

        # Test file removal and saving the session
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        nf = c.process(self.fdata['goodfile'])
        assert_false(os.path.exists(self.fdata['goodfile']['fname']),
            "Cleanup did not remove file")

    def testFacebook(self):
        f = FacebookAction()
        f.cleanup_handler = Mock()
        assert f is not None, "Facebook Action not constructed"
        
        # Test bad facebook session
        assert_false(f.process(self.fdata['badfbsession']))
        assert f.cleanup_handler.queue.put.called,\
            "Did not properly cleanup after facebook failed"
        assert self.fdata['badfbsession']['na'] == na.AUTHENTICATE,\
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
        assert s.cleanup_handler.queue.put.called, \
            "S3 did not clean up local file"
        s.cleanup_handler.queue.put.reset()

        """
        S3 now just tries forever when in this situation
        # Test for when S3 returns an error
        putfxn.return_value.message = '500 Server Error'
        upload(self.fdata['goodfile'])
        assert s.cleanup_handler.queue.put.called, \
            "S3 did not clean up local file"
        s.cleanup_handler.queue.put.reset()
        """

    def testAmazonCovers(self):
        a = AmazonCovers()
        a.cleanup_handler = Mock()
        assert a is not None, "AmazonCovers Action not constructed"

        nf = a.process(self.fdata['goodfile'])
        assert not nf.has_key('swatch')

        nf = a.process(self.fdata['dbrec'])
        assert nf.has_key('swatch')
        assert nf['swatch'] != None and nf['swatch'] != ''
        assert len(a.covercache) > 0

    def testHasher(self):
        h = Hasher()
        h.cleanup_handler = Mock()
        assert h is not None, "Hasher action not constructed"

        # Test an incorrect user sha
        self.fdata['notmp3']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['notmp3']['fname'])
        assert_false(h.process(self.fdata['notmp3']), 
            "Hasher passed a broken file")
        assert h.cleanup_handler.queue.put.called, \
            "Hasher did not clean up broken file"
        h.cleanup_handler.queue.put.reset()

        # Test a correct user sha
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        self.fdata['goodfile'].pop(u'sha')
        nf = h.process(self.fdata['goodfile'])
        assert nf['sha'] != None,\
            "Hasher did not put sha in passed file"

    """
    def testTranscoder(self):
        t = Transcoder()
        t.cleanup_handler = Mock()

        assert t.enabled, \
            'Transcoder not enabled, make sure lame and faad are installed'

        origname = self.fdata['goodmp4']['fname']
        self.fdata['goodmp4']['filetype'] = 'mp4'
        self.fdata['goodmp4']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodmp4']['fname'])
        nf = t.process(self.fdata['goodmp4'])
        assert nf != None, 'Transcoding of mp4 file failed'
        assert nf['fname'] != origname, 'File did not get transcoded'
    """

    def testPuidGenerator(self):
        p = PuidGenerator()
        p.cleanup_handler = Mock()
        assert p, "PuidGenerator not constructed"

        # Test an irrelevant file
        nf = p.process(self.fdata['empty'])

        # Test a good file
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        nf = p.process(self.fdata['goodfile'])
        assert nf['puid'] == '3178113b-858c-2456-f73e-1ab929f38934'

class TestDBActions(TestBase):
    """
    These actions need a database to back them. Since databases are painful
    and slow to set up for unit testing purposes, they get their own class
    """
    def __init__(self, *args):
        super(TestDBActions, self).__init__(*args)
        pconfig['pylons.g'] = Mock()
        pconfig['pylons.g'].sa_engine = engine_from_config(config,
            prefix = 'sqlalchemy.reflect.'
        )
        self.memengine = engine_from_config(config,
            prefix = 'sqlalchemy.default.')
        from masterapp import model
        self.model = model
        model.metadata.bind = self.memengine
        model.Session.configure(bind=self.memengine)

    def setUp(self):
        super(TestDBActions, self).setUp()
        self.model.Session.remove()
        self.model.metadata.create_all()

    def tearDown(self):
        super(TestDBActions, self).tearDown()
        self.model.metadata.drop_all()

    def testDBChecker(self):
        c = DBChecker()
        assert c is not None, "Failed to create dbchecker"
        c.cleanup_handler = Mock()

        # Test creating a user and inserting a brand new file
        nf = c.process(self.fdata['dbrec'])
        assert nf['dbuser'].id is not None,\
            "Failed to insert new user into the database"
        assert nf['dbuser'].fbid == self.fdata['dbrec']['fbid'], \
            "Failed to associate new user with fbid"

        """
        We don't test anymore here since it is all tested with the record
        creation stuff in dbrecorder
        """

    def testDBRecorder(self):
        r = DBRecorder()
        c = DBChecker() #Use this instead of querying for correct results
        assert r is not None, "DBRecorder not constructed"

        # Create our DB user
        user = self.model.User()
        user.fbid = self.fdata['dbrec']['fbid']
        self.model.Session.save(user)
        self.model.Session.commit()
        self.fdata['dbrec']['dbuser'] = user

        # Test insertion of good record
        nf = r.process(self.fdata['dbrec'])
        assert (
            nf['dbownerid'] 
            and nf['dbsongid'] 
            and nf['dbalbumid']
            and nf['dbartistid']
        )
        assert_false(c.process(self.fdata['dbrec']),
            "Checker did not detect clean record insertion")
        assert self.model.Session.query(self.model.Song).get(nf['dbsongid']).title == u'Save Öur City',\
            "DB messed up unicode characters"
        nf.pop('dbownerid')
        nf.pop('dbsongid')
        nf.pop('dbalbumid')
        nf.pop('dbartistid')

        # Test insertion of same record with different user and sha
        self.fdata['dbrec']['sha'] = '256f863d46e7a03cc4f05bab267e313d4b258e01'
        self.fdata['dbrec']['fbid'] = 1908861 
        user = self.model.User()
        user.fbid = self.fdata['dbrec']['fbid']
        self.model.Session.save(user)
        self.model.Session.commit()
        self.fdata['dbrec']['dbuser'] = user
        nf = r.process(self.fdata['dbrec'])
        assert nf['dbownerid'] and nf['dbsongid']
        assert_false(c.process(self.fdata['dbrec']),
            "Checker did not detect duplicate song insertion")
        nf.pop('dbownerid')
        nf.pop('dbsongid')

        # Test insertion of same record with different sha
        self.fdata['dbrec']['sha'] = '1dfbc8174c31551c3f7698a344fe6dc2d6a0f431'
        nf = r.process(self.fdata['dbrec'])
        assert nf['dbownerid'] and nf['dbsongid']
        assert_false(c.process(self.fdata['dbrec']),
            "Checker did not detect duplicate song and user insertion")
        nf.pop('dbownerid')
        nf.pop('dbsongid')

        # Test insertion of incomplete record
        assert_raises(AssertionError, r.process,  self.fdata['goodtags'])

    def testDBTagger(self):
        t = DBTagger()
        assert t, "DBTagger not constructed"

        nf = t.process(self.fdata['dbrec'])
        assert not nf.has_key('dbsongid'), \
            'DBTagger matched something it shouldn\'t have'
