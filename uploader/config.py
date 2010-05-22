from httplib import HTTPConnection

local = dict(server_addr='127.0.0.1', server_port=2985, debug=True, 
			rate_limit=False)

local_test = dict(server_addr='127.0.0.1', server_port=3425, debug=True,
				rate_limit=True)

staging = dict(server_addr='stage.harmonize.fm', server_port=80, debug=False,
				rate_limit=True)

test_server = dict(server_addr='harmonize.fm', server_port=3425, debug=True,
					rate_limit=True)

production = dict(server_addr='harmonize.fm', server_port=80, debug=False,
				rate_limit=True)

current = staging

def get_conn():
	return HTTPConnection(current['server_addr'], current['server_port'])
