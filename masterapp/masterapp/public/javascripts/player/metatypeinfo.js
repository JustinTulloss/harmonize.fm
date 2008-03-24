/* Justin Tulloss - 03/03/2008
 *
 * This file describes all the information about our different metadata types.
 * Right now I think I'm just going to keep it as a global since there's not
 * really a good way to import things in javascript. Instead, everything will
 * just assume that it exists. Let's hope I don't hate myself for that later.
 */

/* TODO: Move all the renderer stuff into its own file. */
t_add_col = new Ext.Template('<img class="mo addtoqueue" src="/images/enqueue.png" />');
var render = {

    enqColumn: function (value, p, record)
    {
        id = record.id;
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


    recColumn: function (value, p, record)
    {
        songid = record.get('songid');    
        albumid = record.get('albumid');
        artist = record.get('artist');
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
        next:'album', 
        display:'Artists',
        gridclass: ArtistGrid
    }, 
    album:{
        next:'song', 
        qry:'albumid', 
        display:'Albums',
        nodeclass: AlbumQueueNode,
        gridclass: AlbumGrid,
    }, 
    playlist:{
        next:'playlistsong', 
        qry:'playlistid', 
        display:'Playlists',
        cm: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: render.enqColumn,
                sortable: false,
            },{
                id:'auto',
                header: "Name",
                dataIndex: 'name'
            },{
                id: 'numtracks',
                header: '# Tracks',
                dataIndex: 'numtracks'
            },{
                id:'length',
                header: 'Length',
                dataIndex: 'totallength'
            }
        ])
    },
    song:{
        next:'play', 
        display:'Songs',
        nodeclass: SongQueueNode,
        gridclass: SongGrid,
    },
    playlistsong:{
        next:'play', 
        display:'Songs'
    },
    friend:{
        next:'artist', 
        qry:'fbid', 
        display:'Friends',
        cm: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: render.enqColumn,
                sortable: false,
            },{
                id:'auto',
                header: "Friend",
                dataIndex: 'name'
            },{
                id:'numartists',
                header: "# Artists",
                dataIndex: 'numartists'
            },{
                id:'numalbums',
                header: "# Albums",
                dataIndex: 'numalbums'
            },{
                id:'likesartists',
                header: "Likes",
                dataIndex: 'likesartists'
            }
        ])
    }
};

//seems like there should be a way to set this above....
typeinfo.friend.cm.defaultSortable = true;
typeinfo.playlist.cm.defaultSortable = true;

/* TODO: Add some playlistsong specific columns */
typeinfo.playlistsong.cm = typeinfo.song.cm;

var fields = ['type', 'title', 'artist', 'album', 'year', 'genre', 
                  'tracknumber', 'totaltracks', 'totalalbums','recs', 
                  'albumlength', 'artistlength', 'numartists','numalbums',
                  'likesartists', 'exartists', 'numtracks', 'name', 'friend',
                  'songid', 'albumid', 'id', 'fbid', 'length', 'playlistid'];

