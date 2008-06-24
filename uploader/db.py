import sqlite3, os
from itunes import get_library_file, ITunes
from hplatform import get_db_path, get_default_path
#some imports at end of program

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

def get_conn():
	global db_dir
	return sqlite3.connect(db_dir)

def get_cursor():
	return get_conn().cursor()

def get_upload_src():
	c = get_cursor()
	return c.execute('select src from upload_src').fetchone()[0]

def set_upload_src(value):
	conn = get_conn()
	c = conn.cursor()
	if value not in ['itunes', 'folder']:
		raise Exception('Invalid upload src')
	c.execute('update upload_src set src=?', (value,))
	conn.commit()

def set_upload_dirs(values):
	conn = get_conn()
	data = [(val,) for val in values]
	c = conn.cursor()
	c.execute('delete from upload_dirs')
	c.executemany('insert into upload_dirs values (?)', data)
	conn.commit()

def get_upload_dirs():
	c = get_cursor()
	values = c.execute('select dir from upload_dirs').fetchall()
	return [val[0] for val in values]

def get_tracks():
	def filter_fn(song):
		return is_music_file(song) and not is_file_uploaded(song)
	src = get_upload_src()
	if src == 'itunes':
		return filter(filter_fn,
					  ITunes().get_all_track_filenames())
	elif src == 'folder':
		tracks = []
		for dir in unique_dirs(get_upload_dirs()):
			tracks.extend(filter(filter_fn, get_music_files(dir)))
		return tracks

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

def set_file_uploaded(filename, puid=None, sha=None):
	conn = get_conn()
	c = conn.cursor()

	c.execute('insert into files_uploaded (filename, puid, sha) values (?,?,?)',
				(filename, puid, sha))
	conn.commit()

def is_file_uploaded(filename):
	c = get_cursor()
	return c.execute(
				'select count(filename) from files_uploaded where filename=?',
				(filename,)).fetchone()[0] > 0

def is_sha_uploaded(sha):
	c = get_cursor()
	return c.execute(
				'select count(sha) from files_uploaded where sha=?', (sha,)).\
				fetchone()[0] > 0

def init_db():
	global db_dir

	conn = get_conn()
	c = conn.cursor()
	c.execute('create table upload_src (src text)')
	c.execute('create table upload_dirs (dir text)')
	c.execute('create table files_uploaded (puid text, filename text,sha text)')

	c.execute('insert into upload_dirs values (?)', (get_default_path(),))

	if get_library_file():
		c.execute('insert into upload_src values (?)', ('itunes',))
	else:
		c.execute('insert into upload_src values (?)', ('folder',))
	
	conn.commit()

db_dir = get_db_path()

if not os.path.exists(db_dir):
	init_db()
else:
	if not get_library_file():
		set_upload_src('folder')
