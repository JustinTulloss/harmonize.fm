from masterapp import model
# The schema that the app is looking for
fields = {
    'song': [
        'type',
        'Friend_id',
        'Friend_name',
        'Song_id',
        'Song_tracknumber',
        'Song_title',
        'Song_length',
        'Song_albumid',
        'Song_artistid',
        'Album_title',
        'Album_totaltracks',
        'Artist_name',
        'Album_asin',
        'Album_mp3_asin'
    ],
    'album': [
        'type',
        'Friend_id',
        'Friend_name',
        'Album_id',
        'Album_title',
        'Album_totaltracks',
        'Album_havesongs',
        'Album_length',
        'Album_year',
        'Album_smallart',
        'Album_mp3_asin',
        'Album_asin',
        'Artist_name'
    ],
    'artist': [
        'type',
        'Friend_id',
        'Friend_name',
        'Artist_id',
        'Artist_name',
        'Artist_sort',
        'Artist_numalbums',
        'Artist_availsongs'
    ],
    'playlist': [
		'type',
		'Friend_id',
        'Friend_name',
		'Playlist_name',
		'Playlist_id',
		'Playlist_songcount',
		'Playlist_length'
	],
    'friend': [
        'type',
        'Friend_id',
        'Friend_name',
        'Friend_songcount',
        'Friend_albumcount',
        'Friend_tastes'
    ],
    'spotlight': [
        'type',
        'Friend_id',
        'Friend_name',
        'Spotlight_id',
        'Spotlight_comment',
        'Album_id',
        'Album_title',
        'Album_smallart',
        'Artist_id',
        'Artist_name'
    ],
}

dbfields = {}
for k, v in fields.items():
    cols = []
    for column in v:
        try:
            klass, field = column.split('_',1)
            if hasattr(model, klass):
                entity = getattr(model, klass)
                if hasattr(entity, field):
                    cols.append(getattr(entity, field).label(column))
        except ValueError:
            pass
    dbfields[k] = cols

