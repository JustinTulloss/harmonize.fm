/* Define all our columns. This will also be read by the server to determine
 * what to send to the client
 */

var BrowserColumns = {
    'Song_tracknumber': {
        id: 'tracknumber', 
        header: "Track",
        width: 60,
        renderer: render.availColumn,
        dataIndex: 'Song_tracknumber'
    },
    'Song_title': {
        id: 'title', 
        header: "Title",
        dataIndex: 'Song_title'
    }, 
    'Song_length': {
        id:'length',
        header: "Length",
        renderer: render.lengthColumn,
        width: 60,
        dataIndex: 'Song_length'
    },
    'Album_title': {
        id: 'album',
        header: 'Album',
        sortable: true,
        width: 200,
        dataIndex: 'Album_title'
    },
    'Album_year': {
        id: 'year',
        header: "Year",
        width: 50,
        dataIndex: 'Album_year'
    },
    'Album_length': {
        id:'album_playtime',
        header: "Total Time",
        renderer: render.lengthColumn,
        dataIndex: 'Album_length'
    },
    'Album_availsongs': {
        id:'num_tracks',
        header: "Tracks",
        dataIndex: 'Album_havesongs',
        renderer: render.availColumn
    },
    'Artist_name': {
        id: 'artist',
        header: 'Artist',
        sortable: true,
        width: 200,
        dataIndex: 'Artist_name'
    },
    'Artist_numalbums': {
        id:'num_albums',
        header: "Albums",
        dataIndex: 'Artist_numalbums'
    },
    'Artist_availsongs': {
        id:'num_tracks',
        header: "Songs",
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
    'Playlist_numtracks': {
        id: 'numtracks',
        header: 'Tracks',
        dataIndex: 'Playlist_numtracks'
    },
    'Playlist_length': {
        id:'length',
        header: 'Length',
        dataIndex: 'Playlist_length'
    },
    'Friend_name': {
        id:'friend',
        header: "Friend",
        dataIndex: 'Friend_name'
    },
    'Friend_numartists': {
        id:'numartists',
        header: "# Artists",
        dataIndex: 'Friend_numartists'
    },
    'Friend_numalbums': {
        id:'numalbums',
        header: "# Albums",
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
        renderer: render.enqColumn,
        width: 55,
        sortable: false
    },
    'expander': new Ext.grid.RowExpander()
};

var ColConfig = {
    song: [
        BrowserColumns['actions'], 
        BrowserColumns['Song_tracknumber'], 
        BrowserColumns['Song_title'], 
        BrowserColumns['Artist_name'], 
        BrowserColumns['Album_title'], 
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
    playlist: [],
    friend: [
        BrowserColumns['actions'], 
        BrowserColumns['Friend_name'],
        BrowserColumns['Friend_numalbums'],
        BrowserColumns['Friend_likes']
    ]
};

