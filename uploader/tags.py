import mutagen.id3 as id3
import tempfile, os

def file_contents_without_tags(filename):
	fd, temp_path = tempfile.mkstemp()
	file_obj = open(temp_path, 'w+b')
	file_obj.write(open(filename, 'rb').read())
	file_obj.flush()

	#id3.delete(temp_path)
	
	file_obj.seek(0)
	file_contents =  file_obj.read()
	file_obj.close()
	
	os.close(fd)
	os.remove(temp_path)
	return file_contents
