/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 */

function Browser(fields)
{
    
    // create the Data Store
    this.ds = new Ext.data.JsonStore({
        url:'metadata',
        root: 'data',
        successProperty: 'success',
        fields:fields
    });

    // the column model has information about grid columns
    // dataIndex maps the column to the specific data field in
    // the data store
    var cm = {
        song:new Ext.grid.ColumnModel([
            {  
                id: 'add',
                header: 'Add',
                renderer: enqColumn,
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
                renderer: starColumn,
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
                renderer: lengthColumn,
                dataIndex: 'length',
            }]),
        album: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: enqColumn,
                sortable: false
            },{
                id:'auto',
                header: "Album",
                dataIndex: 'album'
            },{
                id: 'like',
                header: "Liked",
                renderer: starColumn,
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
                renderer: lengthColumn,
                dataIndex: 'albumlength',
            },{
                id:'num_tracks',
                header: "Total Tracks",
                dataIndex: 'totaltracks',
            },{
                id:'recommend',
                header: 'Recommend',
                renderer: recColumn,
                dataIndex: 'albumid'
            }]),
        artist: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: enqColumn,
                sortable: false,
            },{
                id:'auto',
                header: "Artist",
                dataIndex: 'artist'
            },{
                id: 'like',
                header: "Liked",
                renderer: starColumn,
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
                renderer: recColumn,
                dataIndex: 'artist'
 
            }
        ]),
        friend: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: enqColumn,
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
        ]),
        playlist: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: enqColumn,
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
        ]),
    };

    //seems like there should be a way to set this above....
    cm.song.defaultSortable = true;
    cm.album.defaultSortable = true;
    cm.artist.defaultSortable = true;
    cm.friend.defaultSortable = true;
    cm.playlist.defaultSortable = true;

    cm.playlistsong = cm.song;
    // create the editor grid
    this.grid = new Ext.grid.GridPanel({
        ds: this.ds,
        cm: cm.song,
        selModel: new Ext.grid.RowSelectionModel(),
        enableColLock:false,
        enableDragDrop: true,
        loadMask: true,
        autoExpandColumn: 'auto',
        trackMouseOver: false
    });

    /**** Custom renderers ***/
    function enqColumn(value, p, record)
    {
        id = record.id;
        return '<center><img onclick="enqueue(\''+id+'\')" class="mo" src="/images/enqueue.png" /></center>';
    }

    function starColumn(value, p, record)
    {
        //figure out opacity from record.recs (or something like that)
        recs = record.get('recs')
        opacity = 0
        if (recs != 0)
            opacity = record.get('recs')/record.store.sum('recs');  
        return '<center><img style="opacity:'+opacity+'" src="/images/star.png" /></center>';
    }

    function lengthColumn(value, p, record)
    {
        //Value is the length in milliseconds
        value = Math.floor(value/1000);
        var secs = digitize(value % 60);
        var mins = Math.floor(value / 60 % (60*60));
        var hrs = Math.floor(value / (60*60));

        time = String.format("{0}:{1}", mins, secs);
        if (hrs>0) {
            mins = digitize(mins);
            time = String.format("{0}:{1}:{2}", hrs, mins, secs);
        }
        return time;
    }


    function recColumn(value, p, record)
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

    function digitize(value)
    {
        if (value<10)
            return String.format("0{0}", value);
        else return value;
    }    

    /***** public functions ****/
    this.recommend = recommend;
    function recommend(type, id)
    {
        var connect = new Ext.data.Connection({
            url:'/player/add_rec',
        });
        connect.request({
            params:{'id':id,
                    'type':type}
        });            
        
    }    
    this.changeColModel = changeColModel;
    function changeColModel(type)
    {
        this.grid.reconfigure(this.ds, cm[type]);
        this.grid.getView().fitColumns(true);
    }
}
