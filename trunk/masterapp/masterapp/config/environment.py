"""Pylons environment configuration"""
import os
import sys

from pylons import config

import masterapp.lib.app_globals as app_globals
import masterapp.lib.helpers
from masterapp.config.routing import make_map

from sqlalchemy import engine_from_config

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    sys.path.insert(0,os.path.join(root, '..','..', 'libs.py'))

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='masterapp',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.g'] = app_globals.Globals()
    config['pylons.h'] = masterapp.lib.helpers

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']
    tmpl_options['mako.input_encoding'] = 'UTF-8'
    tmpl_options['mako.output_encoding'] = 'UTF-8'
    tmpl_options['mako.default_filters'] = ['decode.utf8']

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    config['pylons.g'].sa_engine = \
        engine_from_config(config, 'sqlalchemy.default.')

    #Starting extra processing threads here
    from fileprocess.fileprocess import FileUploadThread
    fuploader = FileUploadThread()

