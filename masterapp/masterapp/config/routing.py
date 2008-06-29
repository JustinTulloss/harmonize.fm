"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('error/:action/:id', controller='error')

    # CUSTOM ROUTES HERE
    
    # Upload reroutes
    map.connect('desktop_redirect', controller='upload', 
		action='desktop_redirect', conditions=dict(method=['GET']))
    map.connect('desktop_login', controller='upload', 
		action='desktop_login', conditions=dict(method=['GET']))
    map.connect('upload_ping', controller='upload', 
		action='upload_ping', conditions=dict(method=['GET']))

    # The recommender needs an id and a friend
    map.connect('recommend/:action/:entity/:friend', controller='recommend', 
        requirements=dict(id='\d+', friend='\d+'))
    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')

    return map
