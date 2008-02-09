import os, simplejson
import os.path as path

def update_actions(actions):
	actions['get_dir_listing'] = get_dir_listing

def contains_dir(dir_path):
    if not os.access(dir_path, os.R_OK):
        return False
    for file in os.listdir(dir_path):
        if path.isdir(path.join(dir_path, file)):
            return True
    return False

def get_dir_listing(c):
	request_dir = c.post_query['node'][0]
	new_dirs = [dir for dir in os.listdir(request_dir) if path.isdir(path.join(request_dir, dir))]

	node_list = []
	for dir in new_dirs:
		dir_path = path.join(request_dir, dir)
		new_node = {}
		new_node['text'] = dir
		new_node['id'] = dir_path
		if not contains_dir(dir_path):
			new_node['leaf'] = True
		node_list.append(new_node)

	return simplejson.dumps(node_list)
