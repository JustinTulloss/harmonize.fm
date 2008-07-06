from hfile import HFile, HFileException
import os.path as path

files = ['mp3_file.mp3', 'no_tags.mp3', 'not_an_mp3.mp3', 
			'mp4_file', 'not_an_mp3_bin.mp3', 'no_tags.m4a', 
			'does_not_exist.mp3', 'empty_file.mp3', 'not_an_mp3_bin.m4a',
			'not_an_mp3.m4a', 'no_access.mp3']
abs_files = [path.abspath(path.join('test', file)) for file in files]

for file in abs_files:
	try:
		hfile = HFile(file)
		hfile.contents
		hfile.sha
		hfile.puid
		hfile.tags
		hfile.ppname
	except HFileException, e:
		pass
	except Exception, e:
		import pdb; pdb.set_trace()
