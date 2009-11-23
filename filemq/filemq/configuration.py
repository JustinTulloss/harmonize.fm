# A configuration file for the fileprocess. We could do a .ini, but everybody
# knows python here

import logging
import os
from logging import handlers

config = {
    'port': 48260,
    'S3.accesskey': '17G635SNK33G1Y7NZ2R2',
    'S3.secret': 'PHDzFig4NYRJoKKW/FerfhojljL+sbNyYB9bEpHs',
    'S3.music_bucket': 'music.rubiconmusicplayer.com',
    'S3.upload': True,
    'sqlalchemy.default.convert_unicode': True,
    'upload_dir': '../masterapp/tmp',
    'media_dir': '../masterapp/media',
    'pyfacebook.callbackpath': None,
    'pyfacebook.apikey': 'cec673d0ef3fbc12395d0d3500cd72f9',
    'pyfacebook.secret': 'a08f822bf3d7f80ee25c47414fe98be1',
    'pyfacebook.appid': '2364724122',
    'musicdns.key': 'ffa7339e1b6bb1d26593776b4257fce1',
    'maxkbps': 192000,
    'sqlalchemy.default.url': 'sqlite:///../masterapp/music.db',
    'cache_dir': '../masterapp/cache'
}

dev_config = {
    'S3.upload': False,
    'tagshelf': '../masterapp/tags.archive',
    'exchange': 'fileprocess.dev'
}

test_config = {
    'sqlalchemy.default.url': 'sqlite:///:memory:',
    'sqlalchemy.reflect.url': 'sqlite:///../../masterapp/music.db',
    'upload_dir': './test/testuploaddir',
    'media_dir': './test/teststagingdir',
    'tagshelf': './test/tagshelf'
}

production_config = {
    'S3.upload': True,
    'sqlalchemy.default.url': \
        'mysql://webappuser:gravelbits@localhost:3306/rubicon',
    'sqlalchemy.default.pool_recycle': 3600,
    'upload_dir': '/var/opt/stage_uploads',
    'media_dir': os.environ.get('MEDIA'),
    'tagshelf': '/var/opt/tagshelf.archive',
    'cache_dir': '/tmp/stage_cache',
    'exchange': 'fileprocess.staging'
}

live_config = {
    'port': 48262,
    'upload_dir': '/var/opt/uploads',
    'sqlalchemy.default.url': \
        'mysql://webappuser:gravelbits@localhost:3306/harmonize',
    'cache_dir': '/tmp/live_cache',
    'exchange': 'fileprocess.live'
}

base_logging = {
    'level': logging.INFO,
    'format':'%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s',
    'datefmt': '%H:%M:%S',
    'handler': logging.StreamHandler,
    'handler_args': ()
}

dev_logging = {
    'level': logging.DEBUG
}

production_logging = {
    'level': logging.INFO,
    'handler': handlers.TimedRotatingFileHandler,
    'handler_args': ('/var/log/rubicon/filepipe', 'midnight', 0, 7)
}

live_logging = {
    'handler_args': ('/var/log/harmonize/filepipe', 'midnight', 0, 7)
}

def update_config(nconfig):
    global config
    config.update(nconfig)

def lupdate_config(nconfig):
    global base_logging
    base_logging.update(config)

