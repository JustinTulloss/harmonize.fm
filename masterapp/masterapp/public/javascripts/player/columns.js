/* Define all our columns. This will also be read by the server to determine
 * what to send to the client
 */

var defaultWidths = {
    'Album_title': 225,
    'Artist_name': 175,
    'Song_title': 400
};

var BrowserColumns = {
    'Song_tracknumber': {
        id: 'tracknumber', 
        header: "Track",
        width: 60,
        fixed: true,
        renderer: render.availColumn,
        dataIndex: 'Song_tracknumber'
    },
    'Song_title': {
        id: 'title', 
        width: defaultWidths.Song_title,
        header: "Title",
        dataIndex: 'Song_title'
    }, 
    'Song_length': {
        id:'length',
        header: "Length",
        renderer: render.lengthColumn,
        width: 60,
        fixed: true,
        dataIndex: 'Song_length'
    },
    'Album_title': {
        id: 'album',
        header: 'Album',
        sortable: true,
        width: defaultWidths.Album_title,
        dataIndex: 'Album_title'
    },
    'Album_year': {
        id: 'year',
        header: "Year",
        width: 50,
        fixed: true,
        dataIndex: 'Album_year'
    },
    'Album_length': {
        id:'album_playtime',
        header: "Length",
        renderer: render.lengthColumn,
        fixed: true,
        width: 65,
        dataIndex: 'Album_length'
    },
    'Album_availsongs': {
        id:'num_tracks',
        header: "Tracks",
        width: 65,
        fixed: true,
        dataIndex: 'Album_havesongs',
        renderer: render.availColumn
    },
    'Artist_name': {
        id: 'artist',
        header: 'Artist',
        sortable: true,
        width: defaultWidths.Artist_name,
        dataIndex: 'Artist_name'
    },
    'Artist_numalbums': {
        id:'num_albums',
        width: 60,
        fixed: true,
        header: "Albums",
        css:'text-align: center;',
        dataIndex: 'Artist_numalbums'
    },
    'Artist_availsongs': {
        id:'num_tracks',
        header: "Songs",
        width: 50,
        fixed: true,
        css:'text-align: center;',
        dataIndex: 'Artist_availsongs',
        renderer: render.availColumn
    },
    'Artist_length': {
        id:'artistplaytime',
        header: "Total Time",
        dataIndex: 'Artist_length'
    },
    'Playlist_name': {
        id:'name',
        header: "Name",
        dataIndex: 'Playlist_name'
    },
    'Playlist_songcount': {
        id: 'songcount',
        header: 'Tracks',
        dataIndex: 'Playlist_songcount',
		width: 65,
		fixed: true
    },
    'Playlist_length': {
        id:'length',
        header: 'Length',
        dataIndex: 'Playlist_length',
		width: 65,
        renderer: render.lengthColumn,
		fixed: true
    },
    'Friend_name': {
        id:'friend',
        header: "Friend",
        dataIndex: 'Friend_name'
    },
    'Friend_numartists': {
        id:'numartists',
        width: 60,
        header: "# Artists",
        dataIndex: 'Friend_numartists'
    },
    'Friend_numalbums': {
        id:'numalbums',
        width: 60,
        fixed: true,
        header: "Albums",
        dataIndex: 'Friend_numalbums'
    },
    'Friend_likes': {
        id:'likesartists',
        header: "Likes",
        dataIndex: 'Friend_likes'
    },
    'actions': {  
        id: 'add',
        header: 'Actions',
        css:'text-align: center;',
        renderer: render.enqColumn,
        fixed: true,
        width: 120,
        sortable: false
    },
    'expander': new Ext.grid.RowExpander()
};

var ColConfig = {
    song: [
        BrowserColumns['actions'], 
        BrowserColumns['Song_tracknumber'], 
        BrowserColumns['Song_title'], 
        BrowserColumns['Album_title'], 
        BrowserColumns['Artist_name'], 
        BrowserColumns['Song_length']
    ],
    album: [
        BrowserColumns['expander'],
        BrowserColumns['actions'], 
        BrowserColumns['Album_title'], 
        BrowserColumns['Artist_name'], 
        BrowserColumns['Album_availsongs'], 
        BrowserColumns['Album_length'],
        BrowserColumns['Album_year']
    ],
    artist: [
        BrowserColumns['actions'], 
        BrowserColumns['Artist_name'],
        BrowserColumns['Artist_numalbums'],
        BrowserColumns['Artist_availsongs']
    ],
    playlist: [
		BrowserColumns['actions'],
		BrowserColumns['Playlist_name'],
		BrowserColumns['Playlist_songcount'],
		BrowserColumns['Playlist_length']],
    friend: [
        BrowserColumns['Friend_name'],
        BrowserColumns['Friend_numalbums'],
        BrowserColumns['Friend_likes']
    ]
};

