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
        u'sha': u'344515331e3d1b4389d62dab17d297df4351eddd',
        u'usersha': u'344515331e3d1b4389d62dab17d297df4351eddd',
    },
    'goodpuid' : {
        u'puid': u'ba115bd0-cacb-da69-3240-4608da94e5e6',
    },
	'goodmp4' : {
		u'fname': u'good.m4a'
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
        u'puid': u'd00fe204-528b-3972-4deb-a23d49753323',
        u'artist': u'Dave Matthews Band'
    },
    'amnesiac': {
        u'title': u'Life in a Glass House',
        u'album': u'Amnesiac',
        u'artist': u'Radiohead',
        u'tracknumber': 11,
        u'totaltracks': 11,
        u'duration': 275025,
        u'puid': '88101630-6ea3-e8b6-383f-26f18f546bc6'
    },
    'badtags': {
        u'title': u'Suburban Perfume',
        u'album': u'nihgt at the rit',
        u'artist': u'Office',
        u'puid': u'cb015aca-4640-f886-097c-96a37cfccfd8'
    },
    'incompletetags': {
        u'title': u'Save our city',
        u'artist': u'Ludo',
        u'puid':'90cb3bca-60cd-e567-7bdc-80b1001db5a3'
    },
    'multipleversions': {
        u'title': u'Debra',
        u'artist': u'Beck',
        u'puid': 'ea67e6dc-7928-7965-ab3b-16fcbd6e287a',
        u'duration': 338892.28923518286
    },
    'goodfbsession': {
        u'fbsession': u'08bd66d3ebc459d32391d0d2-1909354'
    },
    'badfbsession': {
        u'fbsession': u'notevenclose to legit'
    },
    'dbpuid': {
        u'fbid': 1909354,
        u'album': u'Broken Bride (Live)', 
        u'mbalbumid': u'defeb27b-ac1d-4d65-a97a-0c45fa4f9710', 
        u'title': u'Save Our City', 
        u'asin': u'B000092ZYX', 
        u'artist': u'Ludo', 
        u'albumartist': u'Ludo',
        u'mbartistid': u'46cf71f5-7583-4834-b843-1f221a41860d', 
        u'mbalbumartistid': u'46cf71f5-7583-4834-b843-1f221a41860d', 
        u'totaltracks': 5, 
        u'length': 396506, 
        u'artistsort': u'Ludo', 
        u'albumartistsort': u'Ludo', 
        u'mbtrackid': u'1e8ee862-a4fe-4595-9a33-b6590bbbc13a', 
        u'tracknumber': 2,
        u'puid':'90cb3bca-60cd-e567-7bdc-80b1001db5a3'
    },
    'dbrec': {
        u'fbid': 1909354,
        u'fname': 'this is needed for things',
        u'size': 386759032,
        u'sha': u'c714a94154d78541f7f9d569ed1b5e56fce7bc8b',
        u'album': u'Broken Bride', 
        u'mbalbumid': u'defeb27b-ac1d-4d65-a97a-0c45fa4f9710', 
        u'title': u'Save Öur City', 
        u'asin': u'B000092ZYX',
        u'mp3_asin': u'B000092ZF4',
        u'artist': u'Ludo', 
        u'albumartist': u'Ludo',
        u'mbartistid': u'46cf71f5-7583-4834-b843-1f221a41860d', 
        u'mbalbumartistid': u'46cf71f5-7583-4834-b843-1f221a41860d', 
        u'totaltracks': 5, 
        u'length': 396506, 
        u'artistsort': u'Ludo', 
        u'albumartistsort': u'Ludo', 
        u'mbtrackid': u'1e8ee862-a4fe-4595-9a33-b6590bbbc13a', 
        u'tracknumber': 2,
        u'puid':'90cb3bca-60cd-e567-7bdc-80b1001db5a3'
    },
    'abird': {
        'album': u'The Mysterious Production of Eggs',
        'artist': u'Andrew Bird',
        'puid': u'9db0e243-c51b-7d89-f542-ac6e55d96cb1',
        'date': u'2005',
        'duration': 68868,
        'title': u'/=/=/',
        'tracknumber': 12,
        'totaltracks': 14,
    },
    'btles2': {
        'album': u'The Beatles (The White Album)',
        'artist': u'The Beatles',
        'composer': u'John Lennon/Paul McCartney',
        'date': u'1968',
        'duration': 182076,
        'genre': u'Rock',
        'title': u'Cry Baby Cry',
        'tracknumber': u'11',
        'puid': u'1623d160-cc36-ea42-9d1b-a1f81058b722'
    },
    'btles1': {
        'album': u'The Beatles (The White Album)',
        'artist': u'The Beatles',
        'composer': u'John Lennon/Paul McCartney',
        'date': u'1968',
        'duration': 163513,
        'genre': u'Rock',
        'title': u'Back in the U.S.S.R.',
        'tracknumber': u'1',
        'puid': u'7a5db316-90df-69d0-8f21-626e9abbbf9d'
    }
}
