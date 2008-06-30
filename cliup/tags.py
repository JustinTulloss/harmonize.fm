#import mutagen.id3 as id3
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3

mp3mapper = {
	'artist': 'artist',
	'album': 'album', 
	'title': 'title',
	'date': 'date',
	'tracknumber': 'tracknumber',
	'genre': 'genre'
}

mp4mapper = {
	'\xa9ART': 'artist',
	'\xa9alb': 'album',
	'\xa9nam': 'title',
	'\xa9day': 'date',
	'\xa9gen': 'genre'
}

def map_tags(song, mapper, tags):
	for key in mapper.keys():
		if song.has_key(key):
			tags[mapper[key]] = song[key][0].encode('utf-8')

def get_tags(filename, puid):
	tags = dict(puid=puid, version='1.0')

	if filename.endswith('.mp3'):
		song = MP3(filename, ID3=EasyID3)
		map_tags(song, mp3mapper, tags)
	else:
		song = MP4(filename)
		map_tags(song, mp4mapper, tags)
		
		if song.has_key('trkn'):
			trkn = song['trkn'][0]
			if type(trkn) == tuple and len(trkn) == 2:
				tags['tracknumber'] = '%s/%s' % trkn
	
	tags['duration'] = int(song.info.length*1000)
	tags['bitrate'] = song.info.bitrate

	return tags
