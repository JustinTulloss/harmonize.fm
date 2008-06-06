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
        if(crumb.ds==null) {
            crumb.ds = new Ext.data.JsonStore({
                url:'metadata',
                root: 'data',
                successProperty: 'success',
                fields:global_config.fields[crumb.type]
            });
        }

        if(params)
            params.type = crumb.type;
        else
            params = {type:crumb.type};

        if (crumb.panel == null) {
            crumb.panel = new typeinfo[crumb.type].gridclass({
                ds: crumb.ds
            });

            crumb.panel.on('render', function(grid) {
                grid.getView().mainBody.on('mousedown', grid.onMouseDown);
            }, this);

            this.fireEvent('newgrid', crumb);
        }

        crumb.ds.load({
            params:params,
            callback: function(){this.fireEvent('chgstatus', null)},
            scope: this
        });
        this.fireEvent('chgstatus', 'Loading...');

    }
}
Ext.extend(Browser, Ext.util.Observable);

function BaseGrid(config)
{
	var my = this;

    config.selModel = new Ext.grid.RowSelectionModel();
    config.bufferResize = true;
    config.enableColLock = false;
    config.enableColumnMove = false;
    config.enableHdMenu = false;
    config.enableDragDrop = true;
    config.ddGroup = 'TreeDD';
    config.loadMask = true;
    config.trackMouseOver = false;
    config.stripeRows = true;
    config.viewConfig = {
        forceFit: true,
        emptyText: 'There isn\'t any music here!<br>'+
            'Upload some, or why not listen to your friends\' music?',
        deferEmptyText: true
    };

    this.addEvents({
        enqueue : true,
        chgstatus: true
    });

    this.actions={
        addtoqueue: function(record) {my.fireEvent('enqueue', [record]);},
		show_spotlight: function(record) {show_spotlight(record);}
    };

    my.onMouseDown = function(e, div) {
        /* XXX: Does this loop scale to lots of actions? */
        for (action in my.actions) {
            if (Ext.get(div).hasClass(action)) {
                e.stopPropagation(); /* Keep this row from getting selected */
				var row = e.getTarget('.x-grid3-row')
				var record = my.getStore().getAt(row.rowIndex);
                my.actions[action](record);
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

    config.cm = new Ext.grid.ColumnModel(ColConfig.song);
    for (var i = 0; i < ColConfig.song.length; i++) {
        if (defaultWidths[ColConfig.song[i].dataIndex])
            config.cm.setColumnWidth(i, defaultWidths[ColConfig.song[i]]);
    }
    config.cm.defaultSortable = true;
    config.autoExpandColumn='title';

    SongGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.getStore().filter('Song_title', text, true, false);
        return true;
    }
}
Ext.extend(SongGrid, BaseGrid);

function AlbumGrid(config)
{
    this.addEvents({
        newgridbranch : true
    });


    exp = BrowserColumns.expander;
    exp.scope = this;
    exp.remoteDataMethod = load_details;
    config.iconCls = 'icon-grid';
    config.plugins = exp;
    config.cm = new Ext.grid.ColumnModel(ColConfig.album);
    for (var i = 0; i < ColConfig.album.length; i++) {
        if (defaultWidths[ColConfig.album[i].dataIndex])
            config.cm.setColumnWidth(i, defaultWidths[ColConfig.album[i]]);
    }
    config.cm.defaultSortable = true;

    AlbumGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.getStore().filter('Album_title', text, true, false);
        return true;
    }
    
    function load_details(record, index)
    {
        var el = Ext.get("remData"+index);
        el.load({
            url: 'player/album_details',
            callback: function(){ this.fireEvent('chgstatus', null) },
            scope: this,
            params: {album:record.get('Album_id')}
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

    config.cm = new Ext.grid.ColumnModel(ColConfig.artist);
    config.cm.defaultSortable = true;
    //config.autoExpandColumn='artist';

    ArtistGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.getStore().filter('Artist_name', text, true, false);
        return true;
    }
}
Ext.extend(ArtistGrid, BaseGrid);

function PlaylistGrid(config)
{
    this.addEvents({
        newgridbranch: true
    });

    config.cm = new Ext.grid.ColumnModel(ColConfig.playlist);
    config.cm.defaultSortable = true;

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
    config.cm = new Ext.grid.ColumnModel(ColConfig.friend);
    config.cm.defaultSortable = true;

    FriendGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.getStore().filter('Friend_name', text, true, false);
        return true;
    }
}
Ext.extend(FriendGrid, BaseGrid);
