#Controller for creating and keeping track of playlist data

from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import User, Session, Playlist
from masterapp.lib.decorators import *
from masterapp.config.schema import dbfields

from sqlalchemy.sql import or_, and_

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
			abort(400)

	def save(self):
		if not (request.params.has_key('playlist') or\
				request.params.has_key('songs')):
			abort(400, 'playlist or songs parameter not provided')

		user = Session.query(User).get(session['userid'])

		playlist = int(request.params['playlist'])
		playlistobj = Session.query(Playlist).\
						filter(and_(Playlist.id == playlist, 
								Playlist.ownerid == session['userid'])).first()
		if not playlistobj:
			abort(400)

		songs = request.params['songs']

		old_pl_songs = playlistobj.songs
		for old_pl_song in old_pl_songs:
			Session.delete(old_pl_song)
		Session.commit()

		if songs != '':
			i=0
			for song in songs.split(','):
				try:
					songid = int(song)
					if not user.get_song_by_id(songid):
						raise ValueError
				except ValueError:
					abort(404)
				pl_song = PlaylistSong(playlist, i, songid)
				pl_song.playlist = playlistobj
				Session.save(pl_song)
				i += 1

		Session.commit()
		return '1'

	def delete(self, id):
		playlist = Session.query(Playlist).get(int(id))
		if playlist.ownerid != session['userid']:
			abort(404, 'Cannot delete another man\'s playlist!')
		Session.delete(playlist)
		Session.commit()
		return '1'
