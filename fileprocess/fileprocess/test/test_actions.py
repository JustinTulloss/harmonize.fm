# -*- coding: utf8 -*-
# vim:expandtab:smarttab
import unittest
import logging
import cPickle as pickle
import nose
from nose.tools import *
from mockfiles import mockfiles
from fileprocess.actions import *
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
        logging.basicConfig(level=logging.DEBUG)
        config.update(dev_config)
        config.update(test_config)

    def setUp(self):
        os.mkdir(config['media_dir'])
        shutil.copytree('./test/testfiles', config['upload_dir'])

        self.fdata = mockfiles.copy()
        for key,f in mockfiles.iteritems():
            self.fdata[key]=f.copy()

    def tearDown(self):
        shutil.rmtree(config['upload_dir'])
        shutil.rmtree(config['media_dir'])
        if os.path.exists(config['tagshelf']):
            os.remove(config['tagshelf'])

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
        assert nf.has_key('tracknumber'), "Did not tag tracknumber"
        assert not "/" in nf['tracknumber'], "Slash exists in tracknumber:" + nf['tracknumber']

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
        #assert u"Ritz" in nf['album'], "Brainz did not correct album"
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
        #assert nf['album'] == u'The Beatles (disc 2)', "Cry baby not on disc 2"
        assert nf.has_key('mbtrackid'), "Did not match Cry Baby Cry"

        nf = b.process(self.fdata['btles1'])
        #assert nf['album'] == u'The Beatles (disc 1)', "USSR not on disc 1"
        assert nf.has_key('mbtrackid'), "Did not match USSR"

    def testCleanup(self):
        c = Cleanup()
        assert c is not None, "Cleanup not constructed"

        # Test file removal and saving the session
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        nf = c.process(self.fdata['goodfile'])
        assert_false(os.path.exists(self.fdata['goodfile']['fname']),
            "Cleanup did not remove file")

    """
    We started doing this in the upload controller.
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
    """

    def testS3(self):
        s = S3Uploader()
        assert s is not None, "S3 uploader not constructed"
        s.cleanup_handler = Mock()

        config['S3.upload'] = True

        # Monkey patch the actual upload function
        putfxn = Mock()
        putfxn.return_value = sentinel
        putfxn.return_value.message = '200 OK'
        import S3
        @patch(S3.AWSAuthConnection, 'put', putfxn)
        def upload(file):
            s.process(file)

        # Test an already uploaded file 
        nf = upload(self.fdata['neupload'])
        assert not putfxn.called, "Uploaded an already uploaded file"

        # Test a good file
        self.fdata['goodfile']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodfile']['fname'])
        upload(self.fdata['goodfile'])
        assert putfxn.called, "S3 did not upload file"
        #assert s.cleanup_handler.queue.put.called, \
        #    "S3 did not clean up local file"
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
        assert nf['asin'] in a.covercache
    
    def testAmazonASINConvert(self):
        a = AmazonASINConvert()
        a.cleanup_handler = Mock()
        assert a is not None, "AmazonASINConvert Action not constructed"

        nf = a.process(self.fdata['goodfile'])
        assert not nf.has_key('mp3_asin')

        nf = a.process(self.fdata['dbrec'])
        assert nf.has_key('mp3_asin')
        assert nf['mp3_asin'] != None
        assert nf['album'] in a.cache

    def testCheckForBadAsin(self):
        a = CheckForBadAsin()
        a.cleanup_handler = Mock()
        assert a is not None, "CheckForBadAsin Action is not constructed"

        nf = a.process(self.fdata['dbrec'])
        assert nf.has_key('asin')
        assert nf['asin'] in a.cache


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

    def testTranscoder(self):
        t = Transcoder()
        t.cleanup_handler = Mock()

        assert t.enabled, \
            'Transcoder not enabled, make sure lame and faad are installed'

        origname = self.fdata['goodmp4']['fname']
        origsha = self.fdata['goodmp4']['usersha'] = 'asdf'
        self.fdata['goodmp4']['fbid'] = '123'
        dir_name = \
            os.path.join(config['upload_dir'], self.fdata['goodmp4']['fbid'])
        print 'dir_name:', dir_name
        os.mkdir(dir_name)
        self.fdata['goodmp4']['filetype'] = 'mp4'
        self.fdata['goodmp4']['fname'] = \
            os.path.join(config['upload_dir'], self.fdata['goodmp4']['fname'])
        nf = t.process(self.fdata['goodmp4'])
        assert nf != False, 'Transcoding of mp4 file failed'
        assert nf['fname'] != origname, 'File did not get transcoded'
        assert nf['usersha'] != origsha, 'sha did not get updated'
        assert nf['fname'].endswith(nf['usersha']), \
                'File did not get renamed correctly'
        os.remove(nf['fname'])
        os.rmdir(dir_name)

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
        assert nf.get('puid') == '04491081-b155-4866-eb96-72adf61b4047'

    def testTagSaver(self):
        s = TagSaver()
        assert s, "TagSaver not constructed"

        # Test an average set of tags
        nf = s.process(self.fdata['goodtags'])
        assert os.path.exists(config['tagshelf']), "Did not create tagshelf"
        shelf = open(config['tagshelf'], 'rb')
        sf = pickle.load(shelf)
        assert sf == nf, "Tags not properly saved off"

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
        assert nf['dbuserid'] is not None,\
            "Failed to insert new user into the database"
        user = self.model.Session.query(self.model.User).get(nf['dbuserid'])
        assert user.fbid == self.fdata['dbrec']['fbid'], \
            "Failed to associate new user with fbid"

        """
        We don't test anymore here since it is all tested with the record
        creation stuff in dbrecorder
        """

    def _create_user(self, key):
        # Create our DB user
        user = self.model.User(self.fdata['fbrec']['fbid'])
        self.model.Session.save(user)
        self.model.Session.commit()
        self.fdata[key]['dbuserid'] = user.id

    def testDBRecorder(self):
        r = DBRecorder()
        c = DBChecker() #Use this instead of querying for correct results
        assert r is not None, "DBRecorder not constructed"

        self._create_user('dbrec')

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
        self._create_user('dbrec')
        nf = r.process(self.fdata['dbrec'])
        assert nf == False
        assert_false(c.process(self.fdata['dbrec']),
            "Checker did not detect duplicate song insertion")

        # Test insertion of same record with different sha
        self.fdata['dbrec']['sha'] = '1dfbc8174c31551c3f7698a344fe6dc2d6a0f431'
        nf = r.process(self.fdata['dbrec'])
        assert nf == False
        assert_false(c.process(self.fdata['dbrec']),
            "Checker did not detect duplicate song and user insertion")

        # Test insertion of a record with the same PUID but different tags
        self._create_user('dbpuid')
        nf = r.process(self.fdata['dbpuid'])
        assert nf != False
        assert_false(c.process(self.fdata['dbpuid']),
            "Checker did not detect duplicate puid insertion")
        assert nf.get('sha') != None, "Did not fill in sha from other song"

        # Test insertion of incomplete record
        assert_raises(AssertionError, r.process,  self.fdata['goodtags'])

    """
    Not using dbtagger anymore
    def testDBTagger(self):
        t = DBTagger()
        t.cleanup_handler = Mock()
        assert t, "DBTagger not constructed"

        self._create_user('dbrec')
        # Test a record we clearly do not have
        nf = t.process(self.fdata['dbrec'])
        assert not nf.has_key('dbsongid'), \
            'DBTagger matched something it shouldn\'t have'

        self._create_user('btles2')
        # Insert a record to be matched
        cry = self.model.Song(
            tracknumber = self.fdata['btles2']['tracknumber'],
            title = self.fdata['btles2']['title'],
            length = self.fdata['btles2']['duration']
        )
        disc2 = self.model.Album(
            title = self.fdata['btles2']['album'],
            totaltracks = 11,
            year = self.fdata['btles2']['date']
        )
        beatles = self.model.Artist(
            name = self.fdata['btles2']['artist']
        )
        self.model.Session.add(beatles)
        disc2.artist = beatles
        self.model.Session.add(disc2)
        cry.album = disc2
        cry.artist = beatles
        self.model.Session.add(cry)
        self.model.Session.commit()
        crypuid = self.model.Puid(puid = '1623d160-cc36-ea42-9d1b-a1f81058b722')
        crypuid.song = cry
        self.model.Session.add(crypuid)
        self.model.Session.commit()
        cryid = cry.id

        # Test a record we do have that should be matched
        nf = t.process(self.fdata['btles2'])
        assert nf == False, "DBTagger did not match"
        cry = self.model.Session.query(self.model.Song).get(cryid)
        newowner = self.model.Session.query(self.model.SongOwner).\
            filter(self.model.SongOwner.song == cry).all()
        assert newowner, "A new owner was not put in the database"

        # Test a record we do have, but is not supposed to be matched
        self.fdata['btles2']['duration'] = 10872000
        self.fdata['btles2']['date'] = None
        self.fdata['btles2']['totaltracks'] = 23
        nf = t.process(self.fdata['btles2'])
        assert nf != False, "Match returned on a non-match track"
    """
