import db
import os
import os.path as path

databases = []
db_dir_path = path.join('test', 'databases')
music_path = path.abspath(path.join('test', 'Back In Black'))
music_files = [path.join(music_path, fname) for fname in os.listdir(music_path)]
music_files.sort()

def test_new_db():
	db_path = path.join(db_dir_path, 'non_existent')
	test_db = db.DB(db_path)
	filename = r'C:\MyMusic\AC_DC\Back In Black\01. Hells Bells.mp3'
	test_db.add_skipped(filename)
	assert test_db.is_file_uploaded(filename)
	assert test_db.total_uploaded_tracks() == 0

	assert test_db.upload_src == 'itunes'
	test_db.upload_src = 'folder'
	assert test_db.upload_src == 'folder'

	upload_dirs = [music_path]
	test_db.upload_dirs = upload_dirs
	assert test_db.upload_dirs == upload_dirs

	tracks = test_db.get_tracks()
	tracks.sort()
	assert tracks == music_files

	test_db.set_puid(music_files[0], 'asdf')
	assert test_db.get_puid(music_files[0]) == 'asdf'
	tracks = test_db.get_tracks()
	tracks.sort()
	assert tracks == music_files

	test_db.set_uploaded(music_files[0])
	tracks = test_db.get_tracks()
	tracks.sort()
	assert tracks == music_files[1:]

	del test_db
	test_db = db.DB(db_path)

	test_db.set_uploaded(music_files[1])
	tracks = test_db.get_tracks()
	tracks.sort()
	assert tracks == music_files[2:]

	assert test_db.total_uploaded_tracks() == 2

os.mkdir(db_dir_path)
for database in databases:
	os.copy(database, db_dir_path)

try:
	test_new_db()
finally:
	for dbname in os.listdir(db_dir_path):
		filename = os.path.join(db_dir_path, dbname)
		os.remove(filename)
	os.rmdir(db_dir_path)
