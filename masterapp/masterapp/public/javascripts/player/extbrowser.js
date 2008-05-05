/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 *   > Yeah, that totally worked. This is the primary grid for the app now --JMT
 */

function Browser()
{
    this.addEvents({
        newgrid: true,
        chgstatus: true
    });

    /***** public functions ****/
    this.load = load;
    function load(crumb, params)
    {
        /* TODO:Replace this with logic that specifies fields that are 
         * more specific to the metadata type 
         */
        if(crumb.ds==null) {
            crumb.ds = new Ext.data.JsonStore({
                url:'metadata',
                root: 'data',
                successProperty: 'success',
                fields:fields
            });
        }

        /* load as soon as possible so we can get other work done */
        if(params)
            params.type = crumb.type;
        else
            params = {type:crumb.type};

        crumb.ds.load({
            params:params,
            callback: function(){this.fireEvent('chgstatus', null)},
            scope: this
        });
        this.fireEvent('chgstatus', 'Loading...');

        if (crumb.panel == null) {
            crumb.panel = new typeinfo[crumb.type].gridclass({
                ds: crumb.ds
            });

            crumb.panel.on('render', function(grid) {
                grid.getView().mainBody.on('mousedown', grid.onMouseDown, grid);
            }, this);

            this.fireEvent('newgrid', crumb);
        }
    }
}
Ext.extend(Browser, Ext.util.Observable);

function BaseGrid(config)
{
    config.selModel=new Ext.grid.RowSelectionModel();
    config.enableColLock=false;
    config.enableDragDrop=true;
    config.loadMask=true;
    config.trackMouseOver=false;
    config.stripeRows = true;

    this.addEvents({
        enqueue : true,
        chgstatus: true
    });

    this.actions={
        addtoqueue: function(records) {this.fireEvent('enqueue', records)}
    };

    this.onMouseDown = onMouseDown;
    function onMouseDown(e, div)
    {
        /* XXX: Does this loop scale to lots of actions? */
        for (action in this.actions) {
            if (Ext.get(div).hasClass(action)) {
                e.stopPropagation(); /* Keep this row from getting selected */
                var records = this.getSelectionModel().getSelections();
                this.actions[action].call(this, records);
            }
        }
    }

    /* Override this to get correct per-type behavior */
    this.search = search;
    function search(text) { return true; }

    BaseGrid.superclass.constructor.call(this, config);

}
Ext.extend(BaseGrid, Ext.grid.GridPanel);

function SongGrid(config)
{
    this.addEvents({
        newgridleaf : true
    });

    config.cm = new Ext.grid.ColumnModel([
        stdcols.add,
        {
            id: 'tracknumber', 
            header: "Track",
            width: 30,
            renderer: render.availColumn,
            dataIndex: 'tracknumber'
        },{
            id: 'title', 
            header: "Title",
            dataIndex: 'title'
        }, stdcols.like,
        {
            id: 'artist',
            header: 'Artist',
            sortable: true,
            width: 200,
            dataIndex: 'artist'
        },{
            id: 'album',
            header: 'Album',
            sortable: true,
            width: 200,
            dataIndex: 'album'
        },{
            id:'length',
            header: "Length",
            renderer: render.lengthColumn,
            width: 60,
            dataIndex: 'length'
        }
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn='title';

    SongGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.getStore().filter('title', text, true, false);
        return true;
    }
}
Ext.extend(SongGrid, BaseGrid);

function AlbumGrid(config)
{
    this.addEvents({
        newgridbranch : true
    });

    var expander = new Ext.grid.RowExpander({
        remoteDataMethod: load_details,
        scope: this
    });

    config.iconCls = 'icon-grid';
    config.plugins = expander;
    config.cm = new Ext.grid.ColumnModel([
        expander,
        stdcols.add,
        {
            id:'album',
            header: "Album",
            dataIndex: 'album'
        },
        stdcols.like,
        {
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
            dataIndex: 'albumlength'
        },{
            id:'num_tracks',
            header: "Tracks",
            dataIndex: 'availsongs',
            renderer: render.availColumn
        },{
            id:'recommend',
            header: 'Recommend',
            renderer: render.recColumn,
            dataIndex: 'albumid'
        }
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn='album';

    AlbumGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.getStore().filter('album', text, true, false);
        return true;
    }
    
    function load_details(record, index)
    {
        var el = Ext.get("remData"+index);
        el.load({
            url: 'player/album_details',
            callback: function(){ this.fireEvent('chgstatus', null) },
            scope: this,
            params: {album:record.get('albumid')}
        });
        this.fireEvent('chgstatus', 'Loading...');
    }
}
Ext.extend(AlbumGrid, BaseGrid);

function ArtistGrid(config)
{
    this.addEvents({
        newgridbranch : true
    });

    config.cm = new Ext.grid.ColumnModel([
        stdcols.add,
        {
            id:'artist',
            header: "Artist",
            dataIndex: 'artist'
        },
        stdcols.like,
        {
            id:'num_albums',
            header: "Albums",
            dataIndex: 'totalalbums'
        },{
            id:'num_tracks',
            header: "Songs",
            dataIndex: 'availsongs',
            renderer: render.availColumn
        },{
            id:'artistplaytime',
            header: "Total Time",
            dataIndex: 'artistlength'
        },{
            id:'recommend',
            header: 'Recommend',
            renderer: render.recColumn,
            dataIndex: 'artist'
        }
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn='artist';

    ArtistGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.getStore().filter('artist', text, true, false);
        return true;
    }
}
Ext.extend(ArtistGrid, BaseGrid);

function PlaylistGrid(config)
{
    this.addEvents({
        newgridbranch: true
    });

    config.cm = new Ext.grid.ColumnModel([
        { 
            id:'add',
            header: 'Add',
            renderer: render.enqColumn,
            sortable: false
        },{
            id:'name',
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
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn = 'name';

    PlaylistGrid.superclass.constructor.call(this, config);
}
Ext.extend(PlaylistGrid, BaseGrid);

function PlaylistSongGrid(config)
{
    //TODO: Add some Playlist specific columns
    PlaylistSongGrid.superclass.constructor.call(this, config);
}
Ext.extend(PlaylistSongGrid, SongGrid);

function FriendGrid(config)
{
    config.cm = new Ext.grid.ColumnModel([
        { 
            id:'add',
            header: 'Add',
            renderer: render.enqColumn,
            sortable: false
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
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn = 'friend';

    FriendGrid.superclass.constructor.call(this, config);
}
Ext.extend(FriendGrid, BaseGrid);
