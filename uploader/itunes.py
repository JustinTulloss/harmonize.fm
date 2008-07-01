import xml.parsers.expat as expat
from base64 import b64decode
from urllib import url2pathname
import urllib

class ITunes(object):
	def __init__(self, filename=None):
		#The main stack to store the current level in the xml file
		self.contents = []
		#The current key in the top dict
		self.key_val = None
		#The current function to use to deal with character data
		self.char_handler = None
		#char data can be cut off in the middle, we need to keep track of
		#successive calls to char_data
		self.cur_str = unicode("", "utf-8")
		if filename == None:
			filename = get_library_file()
		self.itunes_data = self.parse_itunes(filename)

	def parse_itunes(self, filename):
		"""Takes in the filename of the iTunes Library file and returns a data 
		structure made up of dicts, lists, ints, and strings that represent the
		data in the file"""
		parser = expat.ParserCreate('utf-8')
		parser.StartElementHandler = self.start_element
		parser.EndElementHandler = self.end_element
		parser.CharacterDataHandler = self.char_data
		itunes_file = open(filename)
		parser.ParseFile(itunes_file)
		itunes_file.close()
		if self.contents == []:
			return None
		else:
			return self.contents[0]

	def get_playlist_by_name(self, name):
		for playlist in self.itunes_data['Playlists']:
			if playlist['Name'] == name:
				return playlist

		return None

	def get_key_playlist(self):
		for playlist in self.itunes_data['Playlists']:
			if playlist['Master'] == True:
				return playlist
		return None

	def get_all_track_filenames(self):
		for name in ('Library', 'Music'):
			playlist = self.get_playlist_by_name(name)
			if playlist != None: break
		if playlist == None:
			playlist = get_key_playlist()

		if playlist == None:
			return []
		else:
			return self.get_playlist_track_filenames(playlist)
	
	def get_playlist_track_filenames(self, playlist):
		track_filenames = []
		for item in playlist['Playlist Items']:
			track_id = item['Track ID']
			track = self.get_track(track_id)
			filename = track.get('Location')
			if not filename: continue
			#for right now, only upload local files
			if filename[:16] == 'file://localhost':
				track_filenames.append(url2pathname(str(filename)[16:]))

		return track_filenames
	
	def get_track(self, id):
		tracks = self.itunes_data['Tracks']
		if type(id) == int:
			return tracks[str(id)]
		else:
			return tracks[id]

	def start_element(self, name, attributes):
		switch = {
			"plist" : self.start_plist,
			"dict" : self.start_dict,
			"array" : self.start_list,
			"integer" : self.start_int,
			"string" : self.start_string,
			"key" : self.start_string, 
			"true" : self.start_true,
			"false" : self.start_false,
			"date" : self.start_string,
			"data" : self.start_data }
		switch[name]()

	def start_plist(self):
		return None

	def start_dict(self):
		new_dict = dict()
		self.add_to_top(new_dict)
		self.contents.append(new_dict)

	def start_list(self):
		new_list = []
		self.add_to_top(new_list)
		self.contents.append(new_list)
			
	def start_int(self):
		self.char_handler = int

	def start_string(self):
		self.char_handler = lambda x: x

	def start_true(self):
		self.add_to_top(True)

	def start_false(self):
		self.add_to_top(False)

	def start_data(self):
		self.char_handler = b64decode

	def end_element(self, name):
		if name in ("array", "dict") and len(self.contents) > 1:
			self.contents.pop()
		if self.char_handler != None:
			result = self.char_handler(self.cur_str)
			self.add_to_top(result)
			self.char_handler = None
			self.cur_str = unicode("", "utf-8")

	def char_data(self, data):
		if self.char_handler != None:
			self.cur_str += data

	def add_to_top(self, result):
		top = peek(self.contents)
		if type(top) == dict:
			if self.key_val == None:
				self.key_val = result
			else:
				top[self.key_val] = result
				self.key_val = None
		elif type(top) == list: #type is list then
			top.append(result)

def peek(stack):
	if len(stack) == 0:
		return None
	else:
		return stack[len(stack)-1]

def get_library_file(searchPath = []):
	"""
	This function is grabbed from Matt Robinson's python iTunes Library and
	modified slightly. Find the original library at 
	http://lazycat.org/backburner.html
	Look in the usual places for the Library XML file and returns None if it
	can't be found
	"""

	# No joy. Make a list of other places to look.
	import os, platform

	# Try the searchPath first.
	if len(searchPath):
	  for item in searchPath:
		  if os.path.isfile(item):
		  	return item
	
	if platform.system() == 'Darwin':
	  # Add the OS X default location.
	  searchPath.append(os.path.join( os.path.expanduser('~'), 
	  					'Music', 'iTunes', 'iTunes Music Library.xml') )
	elif platform.system() == 'Windows':
	  # Default location for "My Documents" is in the User Profile folder
	  searchPath.append(os.path.join( os.environ['USERPROFILE'], 'My Documents',
	  					'My Music', 'iTunes', 'iTunes Music Library.xml') )

	  # I'm awkward - I moved mine, and I need the registry to find out where.
	  # If we can't access the registry, just skip this step.
	  try:
		import win32api, win32con
		regkey = win32api.RegOpenKeyEx( win32con.HKEY_CURRENT_USER, 
		'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders',
		0, win32con.KEY_READ )

		(value, valtype) = win32api.RegQueryValueEx(regkey, 'My Music')
		if valtype == 1: 
			searchPath.append(
				os.path.join(value, 'iTunes', 'iTunes Music Library.xml'))
	  except:
		pass # Occurit faecam
	else:
		return None

	for path in searchPath:
		if os.path.isfile(path):
			return path

	# Couldn't find anything
	return None
