import os, simplejson
import os.path as path

def update_actions(actions):
	actions['get_dir_listing'] = get_dir_listing

def contains_dir(dir_path):
	try:
		for file in os.listdir(dir_path):
			if path.isdir(path.join(dir_path, file)):
				return True
		return False
	except IOError:
		return False #any directory that gives errors is not a directory I want

def get_dir_listing(c):
	request_dir = c.post_query['node'][0]
	node_list = get_dir_listing_aux(request_dir)
	return simplejson.dumps(node_list)

def get_dir_listing_aux(request_dir):
	new_dirs = [dir for dir in os.listdir(request_dir) if \
				path.isdir(path.join(request_dir, dir)) and dir[0] != '.' \
				and os.access(path.join(request_dir, dir), os.R_OK)]

	node_list = []
	for dir in new_dirs:
		dir_path = path.join(request_dir, dir)
		new_node = {}
		new_node['text'] = dir
		new_node['id'] = dir_path
		if not contains_dir(dir_path):
			new_node['leaf'] = True
		if auto_expand(dir_path):
			new_node['children'] = get_dir_listing_aux(dir_path)
			new_node['attributes'] = {'auto_expand':True}
		elif dir_path == get_default_path():
			new_node['attributes'] = {'select':True}
		node_list.append(new_node)
	return node_list

def auto_expand(dir_path):
	final_path = get_default_path()
	return final_path.startswith(dir_path, 0, len(final_path)-1)

#This is just copied from scripts/upload.py
def get_default_path():
	paths = {'posix':os.getenv('HOME'),
		'nt':r'C:\\',
		'mac':path.join(os.getenv('HOME'), 'Music')}
	
	return paths[os.name]
