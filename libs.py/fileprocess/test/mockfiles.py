# -*- coding: utf8 -*-
mockfiles = {
    'empty' : {},
    'neupload' : {
        u'fname': u'nonexistent.mp3',
        u'sha': u'c714a94154d78541f7f9d569ed1b5e56fce7bc8b'
    },
    'goodfile' : {
        u'fname': u'good.mp3',
        u'fbsession': u'08bd66d3ebc459d32391d0d2-1909354',
        u'sha': u'c714a94154d78541f7f9d569ed1b5e56fce7bc8b',
        u'usersha': u'c714a94154d78541f7f9d569ed1b5e56fce7bc8b'
    },
    'notmp3': {
        u'fname': u'notafile.mp3',
        u'usersha': u'c714a94154d78541f7f9d569ed1b5e56fce7bc8b'
    },
    'nonexistenttags': {
        u'title': u'non-existent',
        u'artist': u'some shitty band',
        u'album': u'Even shittier 3'
    },
    'goodtags': {
        u'title': u'#41',
        u'album': u'Crash',
        u'artist': u'Dave Matthews Band'
    },
    'badtags': {
        u'title': u'Suburban Perfume',
        u'album': u'nihgt at the rit',
        u'artist': u'Office'
    },
    'incompletetags': {
        u'title': u'Save our city',
        u'artist': u'Ludo'
    },
    'multipleversions': {
        u'title': u'Happiness is a Warm Gun',
        u'artist': u'The Beatles'
    },
    'goodfbsession': {
        u'fbsession': u'08bd66d3ebc459d32391d0d2-1909354'
    },
    'badfbsession': {
        u'fbsession': u'notevenclose to legit'
    },
    'dbrec': {
        u'fbid': 1909354,
        u'sha': u'c714a94154d78541f7f9d569ed1b5e56fce7bc8b',
        u'album': u'Broken Bride', 
        u'mbalbumid': u'defeb27b-ac1d-4d65-a97a-0c45fa4f9710', 
        u'title': u'Save Öur City', 
        u'asin': u'B000092ZYX', 
        u'artist': u'Ludo', 
        u'mbartistid': u'46cf71f5-7583-4834-b843-1f221a41860d', 
        u'totaltracks': 5, 
        u'length': 396506, 
        u'artistsort': u'Ludo', 
        u'mbtrackid': u'1e8ee862-a4fe-4595-9a33-b6590bbbc13a', 
        u'tracknumber': 2
    }
}
