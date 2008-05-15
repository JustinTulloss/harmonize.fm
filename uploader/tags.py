#import mutagen.id3 as id3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import tempfile, os

def file_contents_without_tags(filename):
	fd, temp_path = tempfile.mkstemp()
	file_obj = open(temp_path, 'w+b')
	file_obj.write(open(filename, 'rb').read())
	file_obj.flush()

	if filename.endswith('.mp3'):
		song = MP3(temp_path)
	else:
		song = MP4(temp_path)
	song.delete()
	
	file_obj.seek(0)
	file_contents =  file_obj.read()
	file_obj.close()
	
	os.close(fd)
	os.remove(temp_path)
	return file_contents
