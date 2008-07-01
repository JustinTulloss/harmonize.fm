import hashlib, os
import tags, genpuid

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
	
	def get_sha(self):
		if self._sha == None:
			self._sha = hashlib.sha1(self.contents).hexdigest()
		return self._sha
	sha = property(get_sha)

	def get_puid(self):
		if self._puid == None:
			self._puid = genpuid.gen(self.name)
			if self._puid == None:
				self._puid = False
		return self._puid
	puid = property(get_puid)

	def get_contents(self):
		if HFile.cached_name != self.name:
			if HFile.cached_contents != None:
				HFile.cached_contents = None
			HFile.cached_name = self.name
			HFile.cached_contents = open(self.name, 'rb').read() 
		return self.cached_contents
	contents = property(get_contents)

	def get_tags(self):
		if self._tags == None:
			self._tags = tags.get_tags(self.name, self.puid)
		return self._tags
	tags = property(get_tags)

	def get_ppname(self):
		"""The pretty print name of the file"""
		if self.tags.has_key('title') and self.tags.has_key('artist'):
			return self.tags['title'] + ' - ' + self.tags['artist']
		elif self.tags.has_key('title'):
			return self.tags['title']
		else:
			return os.path.basename(self.name)
	ppname = property(get_ppname)
