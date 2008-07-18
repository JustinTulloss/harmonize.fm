import hashlib, os
import tags, genpuid
from db import db
from mutagen.mp3 import HeaderNotFoundError
from mutagen.mp4 import MP4StreamInfoError

"""A generic 'Something is wrong with this file' error and indicates it should
   not be uploaded"""
class HFileException(Exception):
	pass

class HFile(object):
	#We only want to keep around one set of file contents to avoid excessive
	#memory overhead
	cached_contents = None
	cached_name = None

	def __init__(self, filename):
		self.name = filename
		self._sha = None
		self._puid = None
		self._contents = None
		self._tags = None
		self._uploaded = None
		self._puid_tags = None
	
	def get_sha(self):
		if self._sha == None:
			self._sha = hashlib.sha1(self.contents).hexdigest()
		return self._sha
	sha = property(get_sha)

	def get_puid(self):
		if self._puid == None:
			self._puid = db.get_puid(self.name)
			if self._puid == None:
				self._puid = genpuid.gen(self.name)
				if self._puid == None:
					self._puid = False
				else:
					db.set_puid(self.name, self._puid)
		if self._puid:
			return self._puid
		else: return None
	puid = property(get_puid)

	def get_contents(self):
		try:
			if HFile.cached_name != self.name:
				if HFile.cached_contents != None:
					HFile.cached_contents = None
				HFile.cached_name = self.name
				HFile.cached_contents = open(self.name, 'rb').read() 
				if HFile.cached_contents == '':
					raise HFileException('File contents empty')
			return self.cached_contents
		except IOError:
			raise HFileException('Unable to read file')
	contents = property(get_contents)

	def get_tags(self):
		if self._tags == None:
			try:
				self._tags = tags.get_tags(self.name)
			except HeaderNotFoundError, e:
				raise HFileException(str(e))
			except MP4StreamInfoError, e:
				raise HFileException(str(e))
		return self._tags
	tags = property(get_tags)

	def get_puid_tags(self):
		if self._puid_tags == None:
			self.tags['puid'] = self.puid
			self._puid_tags = True
		return self.tags
	puid_tags = property(get_puid_tags)

	def get_ppname(self):
		"""The pretty print name of the file"""
		if self.tags.has_key('title') and self.tags.has_key('artist'):
			val = self.tags['title'] + ' - ' + self.tags['artist']
		elif self.tags.has_key('title'):
			val = self.tags['title']
		else:
			return os.path.basename(self.name)
		return val.decode('utf-8')
	ppname = property(get_ppname)

	def get_uploaded(self):
		if self._uploaded == None:
			self._uploaded = db.is_file_uploaded(self.name)
		return self._uploaded
	
	def set_uploaded(self, value):
		if value:
			db.set_uploaded(self.name, self._puid)
	uploaded = property(get_uploaded, set_uploaded)
