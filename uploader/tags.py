import mutagen.id3 as id3
import tempfile, os

def file_contents_without_tags(filename):
	nil, temp_path = tempfile.mkstemp()
	fd = open(temp_path, 'w+b')
	fd.write(open(filename).read())
	fd.flush()

	id3.delete(temp_path)
	
	fd.seek(0)
	file_contents =  fd.read()
	os.remove(temp_path)
	return file_contents
