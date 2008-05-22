dev_config = {
    'S3.upload': False,
    'S3.accesskey': '17G635SNK33G1Y7NZ2R2',
    'S3.secret': 'PHDzFig4NYRJoKKW/FerfhojljL+sbNyYB9bEpHs',
    'S3.music_bucket': 'music.rubiconmusicplayer.com',
    'sqlalchemy.default.url': 'sqlite:///%(here)s/music.db',
    'sqlalchemy.default.convert_unicode': True
}

production_config = {
    'S3.upload': True,
    'sqlalchemy.default.url': \
        'mysql://webappuser:gravelbits@localhost:3306/rubicon',
    'sqlalchemy.default.pool_recycle': 3600
}
