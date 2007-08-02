from paste import httpexceptions
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.config import ConfigMiddleware, CONFIG
from paste.deploy.converters import asbool

from pylons.error import error_template
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from masterapp.config.environment import load_environment
import masterapp.lib.helpers
import masterapp.lib.app_globals as app_globals

from urllib import urlencode
from paste.deploy.converters import asbool

#add path for our own middleware
import sys, os


def local_error_mapper(code, message, environ, global_conf=None, **kw):
    if global_conf is None:
        global_conf = {}
    codes = [401, 403, 404]
    if environ['pylons.routes_dict']['controller'] == 'wiki':
        codes.remove(404)
    if not asbool(global_conf.get('debug')):
        codes.append(500)
    if code in codes:
        from pylons.util import get_prefix
        url = '%s/error/document/?%s' % (get_prefix(environ),
                                urlencode({'message':message,
                                           'code':code}))
        return url
def make_app(global_conf, full_stack=True, **app_conf):
    """Create a WSGI application and return it
    
    global_conf is a dict representing the Paste configuration options, the
    paste.deploy.converters should be used when parsing Paste config options
    to ensure they're treated properly.
    
    """
    # Setup the Paste CONFIG object, adding app_conf/global_conf for legacy code
    conf = global_conf.copy()
    conf.update(app_conf)
    conf.update(dict(app_conf=app_conf, global_conf=global_conf))
    CONFIG.push_process_config(conf)

    # Load our Pylons configuration defaults
    config = load_environment(global_conf, app_conf)
    config.init_app(global_conf, app_conf, package='masterapp')

    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp(config, helpers=masterapp.lib.helpers,
                                   g=app_globals.Globals)
    g = app.globals
    app = ConfigMiddleware(app, conf)
    
    # YOUR MIDDLEWARE
    # Put your own middleware here, so that any problems are caught by the error
    # handling middleware underneath
    
    # If errror handling and exception catching will be handled by middleware
    # for multiple apps, you will want to set full_stack = False in your config
    # file so that it can catch the problems.
    if asbool(full_stack):
        # Change HTTPExceptions to HTTP responses
        app = httpexceptions.make_middleware(app, global_conf)

        #facebook auth stuff
        if conf.has_key('middleware_dir'):
            import sys
            sys.path.insert(0, conf['middleware_dir'])

        from facebook import wsgi
        app = wsgi.create_pylons_facebook_middleware(app, global_conf)

        # Error Handling
        app = ErrorHandler(app, global_conf, error_template=error_template, **config.errorware)
    
        # Display error documents for 401, 403, 404 status codes (if debug is disabled also
        # intercepts 500)
        app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)
    
    # Establish the Registry for this application
    app = RegistryManager(app)
    
    static_app = StaticURLParser(config.paths['static_files'])
    javascripts_app = StaticJavascripts()
    app = Cascade([static_app, javascripts_app, app])
    return app
