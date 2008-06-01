/* Justin Tulloss - 03/03/2008
 *
 * This file describes all the information about our different metadata types.
 * Right now I think I'm just going to keep it as a global since there's not
 * really a good way to import things in javascript. Instead, everything will
 * just assume that it exists. Let's hope I don't hate myself for that later.
 */

/* TODO: Move all the renderer stuff into its own file. */
t_add_col = new Ext.Template('<img class="addtoqueue" src="/images/enqueue.png" />');
t_add_col_alb = new Ext.Template('<img class="addtoqueue" src="/images/enqueue.png" /><img class="show_spotlight" src="/images/spotlight.png" />');
var render = {

    enqColumn: function (value, p, record)
    {
        id = record.id;
		if (record.data.type === 'album')
			return t_add_col_alb.apply();
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
        gridclass: ArtistGrid
    }, 
    album:{
        next: function (row, breadcrumb) {
            var bc = new BcEntry(
                'song', 
                row.get('Album_title'),
                'song'
            );
            breadcrumb.addbreadcrumb(bc);
        },
        lblindex: 'Album_title',
        qryindex:'Album_id', 
        display:'Albums',
        nodeclass: AlbumQueueNode,
        gridclass: AlbumGrid
    }, 
    playlist:{
        next: function (row, breadcrumb) {
            var bc = new BcEntry(
                'playlistsong', 
                row.get('Playlist_name'),
                'playlistsong'
            );
            breadcrumb.addbreadcrumb(bc);
        },
        lblindex: 'Playlist_name',
        qryindex:'Playlist_id', 
        display:'Playlists',
        gridclass: PlaylistGrid
    },
    song:{
        next:'play', 
        lblindex: 'Song_title',
        display:'Songs',
        nodeclass: SongQueueNode,
        gridclass: SongGrid
    },
    playlistsong:{
        next:'play', 
        display:'Songs',
        gridclass: PlaylistSongGrid
    },
    friend:{
        next: function(row){
            urlmanager.goto_url('/profile/'+row.get('Friend_id'));
        },
        qryindex:'Friend_id', 
        display:'Friends',
        gridclass: FriendGrid
    }
};

