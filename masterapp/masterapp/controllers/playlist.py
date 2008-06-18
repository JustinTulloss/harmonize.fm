#Controller for creating and keeping track of playlist data

from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import User, Session, Playlist
from masterapp.lib.decorators import *
from masterapp.config.schema import dbfields

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
