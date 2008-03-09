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
        cm: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: render.enqColumn,
                sortable: false,
            },{
                id:'auto',
                header: "Artist",
                dataIndex: 'artist'
            },{
                id: 'like',
                header: "Liked",
                renderer: render.starColumn,
                sortable: true,
                dataIndex: 'recs'
            },{
                id:'num_albums',
                header: "Total Albums",
                dataIndex: 'totalalbums',
            },{
                id:'num_tracks',
                header: "Total Tracks",
                dataIndex: 'totaltracks',
            },{
                id:'artistplaytime',
                header: "Total Time",
                dataIndex: 'artistlength',
            },{
                id:'recommend',
                header: 'Recommend',
                renderer: render.recColumn,
                dataIndex: 'artist'
            }
        ])
    }, 
    album:{
        next:'song', 
        qry:'albumid', 
        display:'Albums',
        cm: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: render.enqColumn,
                sortable: false
            },{
                id:'auto',
                header: "Album",
                dataIndex: 'album'
            },{
                id: 'like',
                header: "Liked",
                renderer: render.starColumn,
                sortable: true,
                width:'20px',
                dataIndex: 'recs'
            },{
                id: 'artist',
                header: "Artist",
                dataIndex: 'artist'
            },{
                id: 'year',
                header: "Year",
                dataIndex: 'year'
            },{
                id:'album_playtime',
                header: "Total Time",
                renderer: render.lengthColumn,
                dataIndex: 'albumlength',
            },{
                id:'num_tracks',
                header: "Total Tracks",
                dataIndex: 'totaltracks',
            },{
                id:'recommend',
                header: 'Recommend',
                renderer: render.recColumn,
                dataIndex: 'albumid'
            }
        ])
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
        enqueuefxn: function(record)
            {
                /* To call this function, make sure this is the queue */
                title = record.get('title');
                newnode = new QueueNode(title, record, {leaf: true});
                this.root.appendChild(newnode.treenode);
            },
        cm: new Ext.grid.ColumnModel([
            {  
                id: 'add',
                header: 'Add',
                renderer: render.enqColumn,
                width: 25,
                sortable: false
            },{
                id: 'tracknumber', 
                header: "#",
                width: '20px',
                dataIndex: 'tracknumber'
            },{
                id: 'auto', 
                header: "Title",
                dataIndex: 'title'
            },{
                id: 'like',
                header: "Liked",
                renderer: render.starColumn,
                sortable: true,
                width:'20px',
                dataIndex: 'recs'
            },{
                id: 'artist',
                header: 'Artist',
                sortable: true,
                dataIndex: 'artist'
            },{
                id: 'album',
                header: 'Album',
                sortable: true,
                dataIndex: 'album'
            },{
                id:'length',
                header: "Length",
                renderer: render.lengthColumn,
                dataIndex: 'length'
            }
        ])
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
typeinfo.song.cm.defaultSortable = true;
typeinfo.album.cm.defaultSortable = true;
typeinfo.artist.cm.defaultSortable = true;
typeinfo.friend.cm.defaultSortable = true;
typeinfo.playlist.cm.defaultSortable = true;

/* TODO: Add some playlistsong specific columns */
typeinfo.playlistsong.cm = typeinfo.song.cm;

var fields = ['type', 'title', 'artist', 'album', 'year', 'genre', 
                  'tracknumber', 'totaltracks', 'totalalbums','recs', 
                  'albumlength', 'artistlength', 'numartists','numalbums',
                  'likesartists', 'exartists', 'numtracks', 'name', 'friend',
                  'songid', 'albumid', 'id', 'fbid', 'length', 'playlistid'];

