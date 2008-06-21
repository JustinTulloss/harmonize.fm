#Controller for creating and keeping track of playlist data

from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import User, Session, Playlist
from masterapp.lib.decorators import *
from masterapp.config.schema import dbfields

from masterapp.model import (
    Session, 
    User, 
	Song,
	Playlist,
    PlaylistSong)

class PlaylistController(BaseController):
	def __before__(self):
		ensure_fb_session()

	@cjsonify
	def create(self):
		name = request.params.get('name')
		uid = session.get('userid')
		if name and uid:
			playlist = Playlist(name[:255], uid)
			Session.save(playlist)
			Session.commit()
			qry = Session.query(*dbfields['playlist']).\
					filter(Playlist.id == playlist.id)
			json = build_json([qry.one()])
			json['data'][0]['type'] = 'playlist'
			return json
		else:
			return ''

	def save(self):
		if not (request.params.has_key('playlist') or\
				request.params.has_key('songs')):
			return '' #error

		playlist = int(request.params['playlist'])
		songs = request.params['songs']

		old_pl_songs = Session.query(PlaylistSong).\
						filter(PlaylistSong.playlistid == playlist)
		for old_pl_song in old_pl_songs:
			Session.delete(old_pl_song)

		if songs != '':
			i=0
			for song in songs.split(','):
				pl_song = PlaylistSong(playlist, i, int(song))
				Session.save(pl_song)
				i += 1

		Session.commit()
		return ''

	def delete(self, id):
		playlist = Session.query(Playlist).get(int(id))
		if playlist.ownerid != session['userid']:
			abort(406, 'Cannot delete another man\'s playlist!')
		Session.delete(playlist)
		Session.commit()
		return ''
