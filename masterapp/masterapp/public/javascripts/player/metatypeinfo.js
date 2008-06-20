/* Justin Tulloss - 03/03/2008
 *
 * This file describes all the information about our different metadata types.
 * Right now I think I'm just going to keep it as a global since there's not
 * really a good way to import things in javascript. Instead, everything will
 * just assume that it exists. Let's hope I don't hate myself for that later.
 */

/* TODO: Move all the renderer stuff into its own file. */
t_add_col = new Ext.Template('<span class="grid-actions"><img class="addtoqueue" src="/images/enqueue.png" /><img class="play_record" src="/images/control_play_blue.png" /></span>');
t_add_col_alb = new Ext.Template('<span class="grid-actions"><img class="addtoqueue" src="/images/enqueue.png" /><img class="show_spotlight" src="/images/spotlight.png" /><img class="play_record" src="/images/control_play_blue.png" /></span>');
playlist_col = new Ext.Template('<span class="grid-actions"><img class="play_record" src="/images/control_play_blue.png" /></span>');
var render = {

    enqColumn: function (value, p, record)
    {
        id = record.id;
		if (record.get('type') === 'album' && 
				(record.get('Friend_id') === global_config.uid ||
				 record.get('Friend_id') === ''))
			return t_add_col_alb.apply();
		else if (record.get('type') === 'playlist') {
			return playlist_col.apply();
		}
		else
			return t_add_col.apply();
    },

    starColumn: function (value, p, record)
    {
        //figure out opacity from record.recs (or something like that)
        recs = record.get('recs')
        opacity = 0
        if (recs != 0)
            opacity = record.get('recs')/record.store.sum('recs');  
        return '<center><img style="opacity:'+opacity+'" src="/images/star.png" /></center>';
    },

    lengthColumn: function (value, p, record)
    {
        return format_time(value)
    },


    availColumn: function (value, p, record)
    {
        ret = value;
        total = record.get('Album_totaltracks');
        if (total)
            ret = value + ' of ' + total;

        return ret
    },

    recColumn: function (value, p, record)
    {
        songid = record.get('Song_id');    
        albumid = record.get('Album_id');
        artist = record.get('Artist_name');
        if (songid != "")
        {
            type = 'song';
            id = songid;
        }
        else if (albumid != "")
        {
            type = 'album';
            id = albumid;
        }
        else
        {
            type = 'artist';
            id = artist;
            return '<center><img class="mo" onclick="browser.recommend(\''+type+'\',\''+id+'\')" src="/images/recommend.png" unselectable="on"/></center>';    
        }
        return '<center><img class="mo" onclick="browser.recommend(\''+type+'\','+id+')" src="/images/recommend.png" unselectable="on"/></center>';    
    }
}

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
            breadcrumb.addbreadcrumb(bc);
        },
        lblindex: 'Artist_name',
        qryindex: 'Artist_id',
        display:'Artists',
        nodeclass: ArtistQueueNode,
        gridclass: ArtistGrid,
        emptyText: 'There aren\'t any artists here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
    }, 
    album:{
        next: function (row, breadcrumb) {
            var bc = new BcEntry(
                'song', 
                row.get('Album_title'),
                'song'
            );
            bc.row = row;
            breadcrumb.addbreadcrumb(bc);
        },
        lblindex: 'Album_title',
        qryindex:'Album_id', 
        display:'Albums',
        nodeclass: AlbumQueueNode,
        gridclass: AlbumGrid,
        emptyText: 'There aren\'t any albums here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
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
    },
    song:{
        next:'play', 
        lblindex: 'Song_title',
        display:'Songs',
        nodeclass: SongQueueNode,
        gridclass: SongGrid,
        emptyText: 'There isn\'t any music here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
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
                'profile'
            );
            breadcrumb.addbreadcrumb(bc);
            urlm.goto_url('/people/profile/'+row.get('Friend_id'));
        },
        lblindex: 'Friend_name',
        qryindex:'Friend_id', 
        display:'Friends',
        gridclass: FriendGrid,
        emptyText: 'None of your friends are Harmonize.fm users.  Invite them!',
    },
    friend_radio:{
        display: 'FriendRadio',
        nodeclass: FriendRadioQueueNode
    }
};

