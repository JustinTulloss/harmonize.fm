from response import Redirect

def update_actions(actions):
	actions['complete_login'] = complete_login

def complete_login(c):
	c.session_key = c.query['session_key'][0]
	return Redirect('index.html')
