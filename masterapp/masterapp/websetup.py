"""Setup the masterapp application"""
import logging

from paste.deploy import appconfig
from pylons import config

from migrate.versioning import api as mg 
from migrate.versioning.exceptions import DatabaseAlreadyControlledError

from masterapp.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup masterapp here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    try:
        mg.version_control(config['migrate.url'], config['migrate.repo'])
    except DatabaseAlreadyControlledError:
        log.info("DB exists, not versioning it")

    v = mg.version(config['migrate.repo'])
    dbv = mg.db_version(config['migrate.url'], config['migrate.repo'])

    if v != dbv:
        mg.upgrade(config['migrate.url'], config['migrate.repo'])

    if config['populate_model'] == 'true':
        log.info("Populating data")
        import masterapp.lib.populate_model as populate_model
        populate_model.populate()

    log.info("Successfully setup")
