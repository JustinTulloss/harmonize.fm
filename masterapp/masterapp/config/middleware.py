"""Pylons middleware initialization"""
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool

from pylons import config
from pylons.middleware import error_mapper, ErrorDocuments, ErrorHandler, \
    StaticJavascripts
from pylons.wsgiapp import PylonsApp

from masterapp.config.environment import load_environment
from masterapp.middleware.timer import TimerApp

from beaker.middleware import CacheMiddleware, SessionMiddleware
from routes.middleware import RoutesMiddleware

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether or not this application provides a full WSGI stack (by
        default, meaning it handles its own exceptions and errors).
        Disable full_stack when this application is "managed" by
        another WSGI middleware.

    ``app_conf``
        The application's local configuration. Normally specified in the
        [app:<name>] section of the Paste ini file (where <name>
        defaults to main).
    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp()

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)

    from facebook.wsgi import PylonsFacebook, FacebookWSGIMiddleware
    if app_conf['pyfacebook.mock'] == 'true':
        from masterapp.lib.fakefacebook import setup_fake_facebook
        app = setup_fake_facebook(app, app_conf)
    else:
        app = FacebookWSGIMiddleware(app, app_conf, facebook_class=PylonsFacebook)

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, 
                           **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)

    # Establish the Registry for this application
    app = RegistryManager(app)

    # Time requests that are for more than static files
    if app_conf.get('time_requests') == 'true':
        app = TimerApp(app, app_conf)

    # Static files
    javascripts_app = StaticJavascripts()
    static_app = StaticURLParser(config['pylons.paths']['static_files'])
    app = Cascade([static_app, javascripts_app, app])

    return app
