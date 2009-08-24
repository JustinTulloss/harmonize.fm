/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 *   > Yeah, that totally worked. This is the primary grid for the app now --JMT
 */

function Browser() {
    var my = this;

    my.addEvents({
        newgrid: true,
        chgstatus: true
    });

    /***** public functions ****/
    my.load = function load(crumb, params) {
        if (!crumb.ds) {
            crumb.ds = new Ext.data.JsonStore({
                url:'metadata',
                root: 'data',
                successProperty: 'success',
                id: 'id',
                fields:global_config.fields[crumb.type]
            });
        }

        if (params) {
            params.type = crumb.type;
        }
        else {
            params = {type:crumb.type};
        }

        if (!crumb.panel) {
            crumb.panel = new typeinfo[crumb.type].gridclass({
                ds: crumb.ds
            });

            /* No idea why this was here, appears to cause errors
            crumb.panel.on('render', function(grid) {
                grid.getView().mainBody.on('mousedown', grid.onMouseDown);
            }, this);
            */

            this.fireEvent('newgrid', crumb);
        }
        //this is where we set the emptytext to whatever the correct type is
        // for this particular panel (artist, song, album, etc.) 
        // emptyText property is pulled from the typeinfo[] array from metatypinfo.js
        crumb.ds.on('load', function(e) {
            if (crumb.ds.getCount()===0 && crumb.panel.getEl().child('.x-grid-empty')) {
                crumb.panel.getEl().child('.x-grid-empty').update(typeinfo[crumb.type].emptyText);
            }
        });
        crumb.ds.on('datachanged', function(e) {
            if (crumb.ds.getCount()===0 && crumb.panel.getEl().child('.x-grid-empty')) {
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
            else { this.fireEvent('chgstatus', null); }
        };
        viewmgr.search_field.enableKeyEvents = false;
        crumb.ds.load({
            params:params,
            callback: lazy_load,
            scope: this,
            add: true
        });
        this.fireEvent('chgstatus', 'Loading...');
    };

}
Ext.extend(Browser, Ext.util.Observable);

Hfm.browser = new Browser();

Hfm.browser.BaseGrid = Ext.extend(Ext.grid.GridPanel,{
    constructor: function(config) {
        this.config = config;
        config.selModel = new Ext.grid.RowSelectionModel();
        config.bufferResize = true;
        config.enableColLock = false;
        config.enableColumnMove = false;
        config.enableColumnResize = false;
        config.enableHdMenu = false;
        config.enableDragDrop = false;
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
        this.on('rowdblclick', this.descend);
        config.ds.on('load', function(store, records, options){
            if (records[0]) {
                Hfm.breadcrumb.update_display_values(records[0]);
            }
        });

        Hfm.browser.BaseGrid.superclass.constructor.call(this, config);
        Ext.override(Ext.grid.GridView, {
            scrollToTop: Ext.emptyFn // I'm not sure why this is here.
        });
    },

    find_record: function(el) {
        var row = el.findParent('.x-grid3-row');
        var record = this.getStore().getAt(row.rowIndex);
        return record;
    },
    search: function(text) { return true; },

    /* Default descent, but feel free to override for "special" panels */
    descend: function(grid, rowIndex, evnt) {
        var row = this.getStore().getAt(rowIndex);
        var mycrumb = Hfm.breadcrumb.current_view();
        var myinfo = typeinfo[mycrumb.type];

        var url = Hfm.breadcrumb.build_url(Hfm.breadcrumb.current_view());
        url += '=' + row.get(myinfo.qryindex)+ '/' + this.config.nexttype;
        Hfm.urlm.goto_url(url);
    }
});

Hfm.browser.SongGrid = Ext.extend(Hfm.browser.BaseGrid, {
    constructor: function(config) {
        this.addEvents({
            newgridleaf : true
        });
        config.type = 'song';
        config.cm = new Ext.grid.ColumnModel(ColConfig.song);
        for (var i = 0; i < ColConfig.song.length; i++) {
            if (defaultWidths[ColConfig.song[i].dataIndex]) {
                config.cm.setColumnWidth(i, defaultWidths[ColConfig.song[i]]);
            }
        }
        config.cm.defaultSortable = true;
        config.autoExpandColumn='title';
        Hfm.browser.SongGrid.superclass.constructor.call(this, config);
    },
    search: function (text) {
        if (!text) {
            this.getStore().clearFilter();
        }
        else {
            this.getView().scrollToTop();
            this.getStore().filter('Song_title', text, true, false);
        }
        return true;
    },
    descend: function(grid, rowIndex, evnt) {
        var row = this.getStore().getAt(rowIndex);
        Hfm.queue.playgridrow(row);
    }
});

Hfm.browser.AlbumGrid = Ext.extend(Hfm.browser.BaseGrid, {
    constructor: function(config) {
        this.addEvents({
            newgridbranch : true
        });

        function load_details(record, index) {
            var el = Ext.get("remData"+index);
            el.load({
                url: 'player/album_details',
                callback: function(){ this.fireEvent('chgstatus', null); },
                scope: this,
                params: {
                    album:record.get('Album_id'), 
                    friend:record.get('Friend_id')
                },
                add: false
            });
            this.fireEvent('chgstatus', 'Loading...');
        }

        exp = BrowserColumns.expander;
        exp.scope = this;
        exp.remoteDataMethod = load_details;
        config.type = 'album';
        config.nexttype = 'song';
        config.iconCls = 'icon-grid';
        config.plugins = exp;
        config.cm = new Ext.grid.ColumnModel(ColConfig.album);
        for (var i = 0; i < ColConfig.album.length; i++) {
            if (defaultWidths[ColConfig.album[i].dataIndex]) {
                config.cm.setColumnWidth(i, defaultWidths[ColConfig.album[i]]);
            }
        }
        config.cm.defaultSortable = true;

        Hfm.browser.AlbumGrid.superclass.constructor.call(this, config);
    },
    search: function (text) {
        if (!text) {
            this.getStore().clearFilter();
        }
        else {
            this.getView().scrollToTop();
            this.getStore().filter('Album_title', text, true, false);
        }
        return true;
    }
});

Hfm.browser.ArtistGrid = Ext.extend(Hfm.browser.BaseGrid, {
    constructor: function(config) {
        this.addEvents({
            newgridbranch : true
        });
        config.type = 'artist';
        config.nexttype = 'album';
        config.cm = new Ext.grid.ColumnModel(ColConfig.artist);
        config.cm.defaultSortable = true;
        //config.autoExpandColumn='artist';

        Hfm.browser.ArtistGrid.superclass.constructor.call(this, config);
    },
    search: function(text) {
        if (!text) {
            this.getStore().clearFilter();
        }
        else {
            this.getView().scrollToTop();
            this.getStore().filter('Artist_name', text, true, false);
        }
        return true;
    }
});

Hfm.browser.PlaylistGrid = Ext.extend(Hfm.browser.BaseGrid, {
    constructor: function(config) {
        this.addEvents({
            newgridbranch: true
        });
        config.type = 'playlist';
        config.nexttype = 'song';
        config.cm = new Ext.grid.ColumnModel(ColConfig.playlist);
        config.cm.defaultSortable = true;

        Hfm.browser.PlaylistGrid.superclass.constructor.call(this, config);
    },
    descend: function(grid, rowIndex, evnt){
        var row = grid.getStore().getAt(rowIndex);
        Hfm.playlist.open_record(row);
    }
});

Hfm.browser.PlaylistSongGrid = Ext.extend(Hfm.browser.BaseGrid, {
    constructor: function(config) {
        config.type = 'playlistsong';
        //TODO: Add some Playlist specific columns
        Hfm.browser.PlaylistSongGrid.superclass.constructor.call(this, config);
    }
});

Hfm.browser.FriendGrid = Ext.extend(Hfm.browser.BaseGrid, {
    constructor: function(config){
        config.type = 'friend';
        config.cm = new Ext.grid.ColumnModel(ColConfig.friend);
        config.cm.defaultSortable = true;
        Hfm.browser.FriendGrid.superclass.constructor.call(this, config);
    },
    search: function(text) {
        if (!text) {
            this.getStore().clearFilter();
        }
        else {
            this.getView().scrollToTop();
            this.getStore().filter('Friend_name', text, true, false);
        }
        return true;
    },
    descend: function(grid, rowIndex, evnt) {
        var row = grid.getStore().getAt(rowIndex);
        var bc = new Hfm.breadcrumb.Crumb({
            type: 'profile',
            value: row.get('Friend_name'),
            qryvalue: row.get('Friend_id')
        });
        var url = Hfm.breadcrumb.add({crumb: bc, update:true});
        Hfm.urlm.goto_url(url);
    }
});
