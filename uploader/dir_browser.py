import os
import os.path as path

def contains_dir(dir_path):
	try:
		for file in os.listdir(dir_path):
			if path.isdir(path.join(dir_path, file)):
				return True
		return False
	except IOError:
		return False

def get_dir_listing(request_dir):
	ls = [dir for dir in os.listdir(request_dir) if \
			path.isdir(path.join(request_dir, dir)) and dir[0] != '.' \
			and os.access(path.join(request_dir, dir), os.R_OK)]
	ls.sort()
	return ls
