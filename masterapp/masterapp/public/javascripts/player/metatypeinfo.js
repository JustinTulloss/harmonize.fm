/* Justin Tulloss - 03/03/2008
 *
 * This file describes all the information about our different metadata types.
 * Right now I think I'm just going to keep it as a global since there's not
 * really a good way to import things in javascript. Instead, everything will
 * just assume that it exists. Let's hope I don't hate myself for that later.
 */

Hfm.typeinfo = {
    home:{
        display:'Home'
    },
    artist:{
        lblindex: 'Artist_name',
        qryindex: 'Artist_id',
        display:'Artists',
        urlfunc: Hfm.breadcrumb.build_url,
        nodeclass: ArtistQueueNode,
        gridclass: Hfm.browser.ArtistGrid,
        emptyText: 'There aren\'t any artists here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
		actions: [],
        premiumactions: ['enqueue_row', 'playnow'],
		freeactions: [],
        ownactions: ['delrow']
    }, 
    album:{
        lblindex: 'Album_title',
        qryindex:'Album_id', 
        display:'Albums',
        urlfunc: Hfm.breadcrumb.build_url,
        nodeclass: AlbumQueueNode,
        gridclass: Hfm.browser.AlbumGrid,
        emptyText: 'There aren\'t any albums here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
		actions: [],
        premiumactions: ['enqueue_row', 'playnow'],
		freeactions: ['buy'],
        ownactions: ['spotlight', 'friendrec', 'delrow']
    }, 
    playlist:{
        lblindex: 'Playlist_name',
        qryindex:'Playlist_id', 
        display:'Playlists',
        urlfunc: Hfm.breadcrumb.build_url,
        gridclass: Hfm.browser.PlaylistGrid,
		nodeclass: PlaylistQueueNode,
		emptyText: 'There aren\'t any playlists here!<br>'+
            'Create one by clicking "create playlist" in the bottom left corner.',
        actions: [],
        premiumactions: ['enqueue_row', 'playnow'],
		freeactions: [],
        ownactions: ['spotlight', 'friendrec', 'delrow'],
        remove: function(record) { playlistmgr.delete_playlist(record); }
    },
    song:{
        lblindex: 'Song_title',
        qryindex: 'Song_id',
        display:'Songs',
        urlfunc: Hfm.breadcrumb.build_url,
        nodeclass: SongQueueNode,
        gridclass: Hfm.browser.SongGrid,
        emptyText: 'There isn\'t any music here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
        actions: [],
        premiumactions: ['enqueue_row', 'playnow'],
		freeactions: ['buy'],
        ownactions: ['friendrec', 'delrow']
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
        gridclass: Hfm.browser.PlaylistSongGrid
    },
    friend:{
        lblindex: 'Friend_name',
        qryindex:'Friend_id', 
        display:'Friends',
        gridclass: Hfm.browser.FriendGrid,
        urlfunc: Hfm.breadcrumb.build_url,
        emptyText: 'None of your friends are Harmonize.fm users.  Invite them!'
    },
    profile: {
        qryindex: 'Friend_id',
        display: 'Friend',
        urlfunc: function(crumb) {
            return '/people/profile/'+crumb.qryvalue;
        }
    },
    friend_radio:{
        display: 'FriendRadio',
        nodeclass: FriendRadioQueueNode
    }
};

var typeinfo = Hfm.typeinfo; //for backwards compatibilty

