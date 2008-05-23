# A configuration file for the fileprocess. We could do a .ini, but everybody
# knows python here

import logging
from logging import handlers

config = {
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
    'pyfacebook.appid': '2364724122'
}

dev_config = {
    'S3.upload': False,
    'sqlalchemy.default.url': 'sqlite:///../masterapp/music.db',
}

test_config = {
    'sqlalchemy.default.url': 'sqlite:///:memory:',
    'sqlalchemy.reflect.url': 'sqlite:///../masterapp/music.db',
    'upload_dir': './test/testuploaddir',
    'media_dir': './test/teststagingdir'
}

production_config = {
    'S3.upload': True,
    'sqlalchemy.default.url': \
        'mysql://webappuser:gravelbits@localhost:3306/rubicon',
    'sqlalchemy.default.pool_recycle': 3600
}

base_logging = {
    'level': logging.INFO,
    'format':'%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s',
    'datefmt': '%H:%M:%S',
    'handler': logging.StreamHandler,
    'handler_args': ()
}

dev_logging = {
    'level': logging.INFO
}

production_logging = {
    'level': logging.INFO,
    'handler': handlers.TimedRotatingFileHandler,
    'handler_args': ('/var/log/rubicon/filepipe', 'midnight', 0, 7)
}
