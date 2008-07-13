/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 *   > Yeah, that totally worked. This is the primary grid for the app now --JMT
 */

function Browser()
{
    my = this;
    
    this.addEvents({
        newgrid: true,
        chgstatus: true
    });

    /***** public functions ****/
    my.load = function load(crumb, params)
    {
        if(crumb.ds==null) {
            crumb.ds = new Ext.data.JsonStore({
                url:'metadata',
                root: 'data',
                successProperty: 'success',
                id: 'id',
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
        //this is where we set the emptytext to whatever the correct type is
        // for this particular panel (artist, song, album, etc.) 
        // emptyText property is pulled from the typeinfo[] array from metatypinfo.js
        crumb.ds.on('load', function(e) {
            if ((crumb.ds.getCount() == 0) && (crumb.panel.getEl().child('.x-grid-empty'))) {
                crumb.panel.getEl().child('.x-grid-empty').update(typeinfo[crumb.type].emptyText);
            }
        });
        crumb.ds.on('datachanged', function(e) {
            if ((crumb.ds.getCount() == 0) && (crumb.panel.getEl().child('.x-grid-empty'))) {
                crumb.panel.getEl().child('.x-grid-empty').update(typeinfo[crumb.type].emptyText);
            }
        });

    
        var bufferSize = 35; //how many records to grab at a time?        
        
        params.start = 0;
        params.limit = bufferSize;

        var lazy_load = function(r, options, success){
            if (r.length < (params.limit - params.start)) {
                records_remaining = false;
                viewmgr.search_field.enableKeyEvents = true;
            } else {
                records_remaining = true;
                params.start += bufferSize;
                params.limit += bufferSize;   
            }
            if (records_remaining) { 
                crumb.ds.load({
                    params:params,
                    callback: lazy_load,
                    scope: this,
                    add: true            
                });
            }
            else this.fireEvent('chgstatus', null);
        };
        viewmgr.search_field.enableKeyEvents = false;
        crumb.ds.load({
            params:params,
            callback: lazy_load,
            scope: this,
            add: true
        });
        this.fireEvent('chgstatus', 'Loading...');
    }

    my.load_url = function(url) {
        if (url.indexOf('?') != -1) {
            //this means there is a variable somewhere
            url = url.split('?');
            location.vars = url[1];
            url = url[0];
        }
        var parts = url.split('/')
        var params = {};
        var param = null;
        var splice = false;
        for (var i =0; i<parts.length; i++) {
            param = parts[i].split('=');
            var type = param[0];
            var value = null;
            if (param.length == 2) {
                value = param[1]
                params[type] = value;
            }
            var itercrumb = Hfm.breadcrumb.get(i);
            if (itercrumb && itercrumb.type === type && 
                    itercrumb.qryvalue == value) {
                if (itercrumb.row)
                    itercrumb.value = itercrumb.row.get(
                        typeinfo[itercrumb.type].lblindex);
            }
            else {
                var crumb = new Hfm.breadcrumb.Crumb({
                    type: type,
                    queryby: value
                });
                var update = false;
                if (!value)
                    update = true; //Update on the final crumb
                Hfm.breadcrumb.add({index: i, crumb: crumb, update: true});
            }
        }
        //my.fireEvent('bcupdate', bclist[current], params);
        if (!Hfm.breadcrumb.current_view().panel)
            my.load(crumb, params);
        else
            Hfm.view.set_panel(crumb, params);
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
    config.loadMask = false;
    config.trackMouseOver = false;
    config.stripeRows = true;
    config.viewConfig = {
        forceFit: true,
        emptyText: "Loading...",
        deferEmptyText: false
    };
    this.addEvents({
        enqueue : true,
        chgstatus: true
    });

    my.find_record = function(el) {
        var row = el.findParent('.x-grid3-row')
        var record = my.getStore().getAt(row.rowIndex);
        return record
    }

    /* Override this to get correct per-type behavior */
    my.search = function(text) { return true; }

    /* Default descent, but feel free to override for "special" panels */
    my.descend = function(grid, rowIndex, evnt) {
        var row = my.getStore().getAt(rowIndex);
        var mycrumb = Hfm.breadcrumb.current_view();
        var myinfo = typeinfo[mycrumb.type];
        
        mycrumb.row = row;
        mycrumb.qryvalue = row.get(myinfo.qryindex);

        var url = Hfm.breadcrumb.build_url(Hfm.breadcrumb.current_view());
        url += '/'+config.nexttype;
        Hfm.urlm.goto_url(url);
    }
    my.on('rowdblclick', my.descend);

    BaseGrid.superclass.constructor.call(this, config);
    Ext.override(Ext.grid.GridView, {
        scrollToTop: Ext.emptyFn    
    });
}
Ext.extend(BaseGrid, Ext.grid.GridPanel);

function SongGrid(config)
{
    my = this;
    this.addEvents({
        newgridleaf : true
    });
    config.type = 'song';
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
        if (text == "") 
            this.getStore().clearFilter();
        else
            this.getStore().filter('Song_title', text, true, false);
        return true;
    }

    my.descend = function(grid, rowIndex, evnt) {
        var row = my.getStore().getAt(rowIndex);
        Hfm.playrow(row);
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
    config.type = 'album';
    config.nexttype = 'song';
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
        if (text == "")
            this.getStore().clearFilter();
        else
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
            params: {
                album:record.get('Album_id'), 
                friend:record.get('Friend_id')
            },
            add: false
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
    config.type = 'artist';
    config.nexttype = 'album';
    config.cm = new Ext.grid.ColumnModel(ColConfig.artist);
    config.cm.defaultSortable = true;
    //config.autoExpandColumn='artist';
    
    ArtistGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        if (text == "")
            this.getStore().clearFilter();
        else
            this.getStore().filter('Artist_name', text, true, false);
        return true;
    }
}
Ext.extend(ArtistGrid, BaseGrid);

function PlaylistGrid(config)
{
    var my = this;
    this.addEvents({
        newgridbranch: true
    });
    config.type = 'playlist';
    config.nexttype = 'song';
    config.cm = new Ext.grid.ColumnModel(ColConfig.playlist);
    config.cm.defaultSortable = true;
    
    PlaylistGrid.superclass.constructor.call(this, config);
    my.descend = function(grid, rowIndex, evnt){
        var row = row.getStore.getAt(rowIndex);
        Hfm.open_playlist(row);
    }
        
}
Ext.extend(PlaylistGrid, BaseGrid);

function PlaylistSongGrid(config)
{
    config.type = 'playlistsong';
    //TODO: Add some Playlist specific columns
    PlaylistSongGrid.superclass.constructor.call(this, config);
}
Ext.extend(PlaylistSongGrid, SongGrid);

function FriendGrid(config)
{
    var my = this;

    config.type = 'friend';
    config.cm = new Ext.grid.ColumnModel(ColConfig.friend);
    config.cm.defaultSortable = true;
    FriendGrid.superclass.constructor.call(this, config);
    
    my.search = function(text) {
        if (text == "")
            this.getStore().clearFilter();
        else
            this.getStore().filter('Friend_name', text, true, false);
        return true;
    }

    my.descend = function(grid, rowIndex, evnt) {
        var row = row.getStore().getAt(rowIndex);
        var bc = new Hfm.breadcrumb.Crumb({
            type: 'profile',
            value: row.get('Friend_name'),
            queryby: row.get('Friend_id')
        });
        var url = Hfm.breadcrumb.add({crumb: bc, update:true});
        Hfm.urlm.goto_url(url);
    }
}
Ext.extend(FriendGrid, BaseGrid);
