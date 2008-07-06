/* Justin Tulloss - 03/03/2008
 *
 * This file describes all the information about our different metadata types.
 * Right now I think I'm just going to keep it as a global since there's not
 * really a good way to import things in javascript. Instead, everything will
 * just assume that it exists. Let's hope I don't hate myself for that later.
 */

var typeinfo = {
    home:{
        display:'Home'
    },
    artist:{
        next: function (row, breadcrumb) {
            var bc = new BcEntry(
                'album',
                row.get('Artist_name'),
                'album'
            );
            breadcrumb.add_breadcrumb(bc);
        },
        lblindex: 'Artist_name',
        qryindex: 'Artist_id',
        display:'Artists',
        nodeclass: ArtistQueueNode,
        gridclass: ArtistGrid,
        emptyText: 'There aren\'t any artists here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
        actions: ['enqueue', 'playnow'],
        ownactions: ['delrow'],
    }, 
    album:{
        next: function (row, breadcrumb) {
            var bc = new BcEntry(
                'song', 
                row.get('Album_title'),
                'song'
            );
            bc.row = row;
            breadcrumb.add_breadcrumb(bc);
        },
        lblindex: 'Album_title',
        qryindex:'Album_id', 
        display:'Albums',
        nodeclass: AlbumQueueNode,
        gridclass: AlbumGrid,
        emptyText: 'There aren\'t any albums here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
        actions: ['enqueue', 'playnow'],
        ownactions: ['spotlight', 'friendrec', 'delrow'],
    }, 
    playlist:{
        next: 'openplaylist',
        lblindex: 'Playlist_name',
        qryindex:'Playlist_id', 
        display:'Playlists',
        gridclass: PlaylistGrid,
		nodeclass: PlaylistQueueNode,
		emptyText: 'There aren\'t any playlists here!<br>'+
            'Create one by clicking "create playlist" in the bottom left corner.',
        actions: ['enqueue', 'playnow'],
        ownactions: ['spotlight', 'friendrec', 'delrow'],
        remove: function(record) {playlistmgr.delete_playlist(record)}
    },
    song:{
        next:'play', 
        lblindex: 'Song_title',
        qryindex: 'Song_id',
        display:'Songs',
        nodeclass: SongQueueNode,
        gridclass: SongGrid,
        emptyText: 'There isn\'t any music here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
        actions: ['enqueue', 'playnow'],
        ownactions: ['friendrec', 'delrow'],
    },
    nowplayingsong:{
        nodeclass: PlayingQueueNode,
		inactive: true
    },
    prevsong:{
        nodeclass: SongQueueNode,
		inactive: true
    },
    playlistsong:{
        next:'play', 
        display:'Songs',
        gridclass: PlaylistSongGrid
    },
    friend:{
        next: function(row, breadcrumb){
            var bc = new BcEntry(
                'profile',
                row.get('Friend_name'),
                'profile',
                row.get('Friend_id')
            );
            var url = '/people/profile/'+row.get('Friend_id');
            bc.url = url;
            breadcrumb.add_breadcrumb(bc, url);
        },
        lblindex: 'Friend_name',
        qryindex:'Friend_id', 
        display:'Friends',
        gridclass: FriendGrid,
        emptyText: 'None of your friends are Harmonize.fm users.  Invite them!'
    },
    profile: {
        lblindex: 'Friend_name',
        qryindex: 'Friend_id',
        display: 'Friend',
        bcurl: '/people/profile/{0}',
    },
    friend_radio:{
        display: 'FriendRadio',
        nodeclass: FriendRadioQueueNode
    }
};

