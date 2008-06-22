from masterapp import model
# The schema that the app is looking for
fields = {
    'song': [
        'type',
        'Friend_id',
        'Song_id',
        'Song_tracknumber',
        'Song_title',
        'Song_length',
        'Song_albumid',
        'Song_artistid',
        'Album_title',
        'Album_totaltracks',
        'Artist_name'
    ],
    'album': [
        'type',
        'Friend_id',
        'Album_id',
        'Album_title',
        'Album_totaltracks',
        'Album_havesongs',
        'Album_length',
        'Album_year',
        'Album_smallart',
        'Artist_name'
    ],
    'artist': [
        'type',
        'Friend_id',
        'Artist_id',
        'Artist_name',
        'Artist_sort',
        'Artist_numalbums',
        'Artist_availsongs'
    ],
    'playlist': [
		'type',
		'Playlist_name',
		'Playlist_id',
		'Playlist_songcount',
		'Playlist_length',
		'Friend_id'
	],
    'friend': [
        'type',
        'Friend_id',
        'Friend_name',
    ],
    'spotlight': [
        'type',
        'Friend_id',
        'Spotlight_id',
        'Spotlight_comment',
        'Album_id',
        'Album_title',
        'Album_smallart',
        'Artist_id',
        'Artist_name',
    ],
}

dbfields = {}
for k, v in fields.items():
    cols = []
    for column in v:
        try:
            klass, field = column.split('_')
            if hasattr(model, klass):
                entity = getattr(model, klass)
                if hasattr(entity, field):
                    cols.append(getattr(entity, field).label(column))
        except ValueError:
            pass
    dbfields[k] = cols

