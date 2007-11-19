/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 */

function Browser(domObj, fields){
    
    var div = domObj

    // create the Data Store
    this.ds = new Ext.data.JsonStore({
        url:'player/get_data',
        root: 'data',
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
                sortable: false
            },{
                id: 'tracknumber', 
                header: "#",
                dataIndex: 'tracknumber'
            },{
                id: 'title', 
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
               id: 'album',
               header: "Album",
               dataIndex: 'album'
            },{
               id: 'artist',
               header: "Artist",
               dataIndex: 'artist'
            },{
               id: 'recommend',
               header: "Recommend",
               sortable: false,
               renderer: recColumn,
               dataIndex: 'songid'
            }]),
        album: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: enqColumn,
                sortable: false
            },{
                id:'album',
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
                id:'artist',
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
                id:'friend',
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
        genre: new Ext.grid.ColumnModel([
            { 
                id:'add',
                header: 'Add',
                renderer: enqColumn,
                sortable: false,
            },{
                id:'genre',
                header: "Genre",
                dataIndex: 'genre'
            },{
                id:'numartists',
                header: '# Artists',
                dataIndex: 'numartists'
            },{
                id: 'numalbums',
                header: '# Albums',
                dataIndex: 'numalbums'
            },{
                id: 'exartists',
                header: 'Examples',
                dataIndex: 'exartists',
                sortable: false
            }
        ]) 
    };

    //seems like there should be a way to set this above....
    cm.song.defaultSortable = true;
    cm.album.defaultSortable = true;
    cm.artist.defaultSortable = true;
    cm.friend.defaultSortable = true;
    cm.genre.defaultSortable = true;

    // create the editor grid
    this.grid = new Ext.grid.Grid(div, {
        ds: this.ds,
        cm: cm.song,
        selModel: new Ext.grid.RowSelectionModel(),
        enableColLock:false,
        enableDragDrop: true,
        loadMask: true,
        autoSizeColumns: true,
        trackMouseOver: false
    });

    // make the grid resizable, do before render for better performance
    var rz = new Ext.Resizable(div, {
        wrap:true,
        minHeight:100,
        pinned:true,
        handles: 's'
    });
    rz.on('resize', this.grid.autoSize, this.grid);

    // render it
    this.grid.render();

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
