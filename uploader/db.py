import sqlite3, os
from itunes import get_library_file, ITunes
from hplatform import get_db_path, get_default_path

def get_music_files(dir):
	music_files = []
	
	for root, dirs, files in os.walk(dir):
		for file in files:
			if is_music_file(file):
				#trying to catch the special case in Ubuntu where $HOME/Network
				#maps to every network share. You can still upload that dir if
				#you select it explicitly, but it won't descend automatically.
				if not(root == os.getenv('HOME') and file == 'Network' 
					   and os.name == 'posix'):
					music_files.append(os.path.join(root, file))
	
	return music_files

def is_music_file(file):
	return file.endswith('.mp3') or file.endswith('.m4a')

def unique_dirs(dirs):
	unique_dirs = []
	dirs.sort()
	for dir in dirs:
		child_dir = False
		for pdir in unique_dirs:
			if os.path.commonprefix([pdir, dir]) == pdir:
				child_dir = True
				break
		if not child_dir:
			unique_dirs.append(dir)
	
	return unique_dirs

class DB(object):
	def __init__(self, db_path):
		self.db_path = db_path

		self.versions = [self.version_1]

		try:
			conn = self.get_conn()
			version = int(conn.execute('select value from settings where key=?',
									('version',)).fetchone()[0])
		except sqlite3.OperationalError:
			conn.close()
			os.remove(self.db_path)
			version = 0

		for upgrade_version in self.versions[version:]:
			upgrade_version()

	def get_conn(self):
		return sqlite3.connect(self.db_path)

	def version_1(self):
		conn = self.get_conn()
		c = conn.cursor()

		c.execute('create table settings (key text, value text)')
		c.execute('create table upload_dirs (dir text)')
		c.execute('''create table files
					(filename text, puid text, uploaded int)''')
		c.execute('create table files_skipped (filename text)')

		c.execute('insert into settings (key, value) values (?, ?)',
			('version', '1'))
		
		if get_library_file:
			upload_src = 'itunes'
		else:
			upload_src = 'folder'
		c.execute('insert into settings (key, value) values (?, ?)',
			('upload_src', upload_src))

		c.execute('insert into upload_dirs values (?)', (get_default_path(),))

		conn.commit()

	def add_skipped(self, filename):
		conn = self.get_conn()
		conn.execute('insert into files_skipped values(?)', (filename,))
		conn.commit()

	def is_file_uploaded(self, filename):
		c = self.get_conn().cursor()
		return c.execute(
					'''select filename from files where 
							filename=? and uploaded=? union
					   select filename from files_skipped where filename=?''',
					(filename, 1, filename)).fetchone() != None

	def total_uploaded_tracks(self):
		c = self.get_conn()
		return c.execute('select count(*) from files where uploaded=?',
							(1,)).fetchone()[0]

	def get_tracks(self):
		if self.upload_src == 'itunes':
			tracks =  filter(is_music_file,
						  ITunes().get_all_track_filenames())
		else:
			tracks = []
			for dir in unique_dirs(self.upload_dirs):
				tracks.extend(get_music_files(dir))

		if tracks == []:
			return None
		else:
			return filter(lambda x: not self.is_file_uploaded(x), tracks)

	def get_upload_src(self):
		c = self.get_conn()
		return c.execute('select value from settings where key=?',
			('upload_src',)).fetchone()[0]

	def set_upload_src(self, value):
		conn = self.get_conn()
		if value not in ['itunes', 'folder']:
			raise Exception('Invalid upload src')
		conn.execute('update settings set value=? where key=?', 
			(value,'upload_src'))
		conn.commit()

	upload_src = property(get_upload_src, set_upload_src)

	def set_upload_dirs(self, values):
		conn = self.get_conn()
		data = [(val,) for val in values]
		c = conn.cursor()
		c.execute('delete from upload_dirs')
		c.executemany('insert into upload_dirs values (?)', data)
		conn.commit()

	def get_upload_dirs(self):
		c = self.get_conn()
		values = c.execute('select dir from upload_dirs').fetchall()
		return [val[0] for val in values]

	upload_dirs = property(get_upload_dirs, set_upload_dirs)
	
	def get_puid(self, filename):
		c = self.get_conn()
		res = c.execute('select puid from files where filename=?', 
				(filename,)).fetchone()
		if res == None:
			return None
		else:
			return res[0]

	def file_exists(self, filename, conn):
		return (conn.execute('select count(*) from files where filename=?',
							(filename,)).fetchone()[0] > 0)

	def set_puid(self, filename, puid):
		conn = self.get_conn()
		if self.file_exists(filename, conn):
			conn.execute('update files set puid=? where filename=?',
						(puid, filename))
		else:
			conn.execute('''insert into files (filename, puid, uploaded) values
							(?, ?, ?)''', (filename, puid, 0))
		conn.commit()
	
	def set_uploaded(self, filename, puid=None):
		conn = self.get_conn()
		if self.file_exists(filename, conn):
			conn.execute('update files set uploaded=? where filename=?',
							(1, filename))
		else:
			conn.execute('''insert into files (filename, puid, uploaded) values
							(?, ?, ?)''', (filename, puid, 1))
		conn.commit()

db = DB(get_db_path())

def use_new_db(path):
	global db
	db = DB(path)
