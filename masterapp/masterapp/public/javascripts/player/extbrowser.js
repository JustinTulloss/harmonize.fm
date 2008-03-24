/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 *   > Yeah, that totally worked. This is the primary grid for the app now --JMT
 */

function Browser()
{
    this.addEvents({
        newgrid: true
    });

    /***** public functions ****/
    this.load = load;
    function load(crumb, params)
    {
        /* TODO:Replace this with logic that specifies fields that are more specific
         * to the metadata type */
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
        crumb.ds.load({params:params});

        if (crumb.panel == null) {
            crumb.panel = new typeinfo[crumb.type].gridclass({
                ds: crumb.ds,
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

    this.addEvents({
        enqueue : true
    });

    this.actions={
        addtoqueue: function(records) {this.fireEvent('enqueue', records)}
    };

    this.onMouseDown = onMouseDown;
    function onMouseDown(e, div)
    {
        /* XXX: Does this loop scale to lots of actions? */
        for (action in this.browser.actions) {
            if (Ext.get(div).hasClass(action)) {
                e.stopEvent(); /* Keep this row from getting selected */
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
        newgridleaf : true,
    });

    config.cm = new Ext.grid.ColumnModel([
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
            id: 'title', 
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
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn='title';

    SongGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.ds.filter('title', text, true, false);
        return true;
    }
}
Ext.extend(SongGrid, BaseGrid);

function AlbumGrid(config)
{
    this.addEvents({
        newgridbranch : true
    });

    config.cm = new Ext.grid.ColumnModel([
        { 
            id:'add',
            header: 'Add',
            renderer: render.enqColumn,
            sortable: false
        },{
            id:'album',
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
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn='album';

    AlbumGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.ds.filter('album', text, true, false);
        return true;
    }
}
Ext.extend(AlbumGrid, BaseGrid);

function ArtistGrid(config)
{
    this.addEvents({
        newgridbranch : true
    });

    config.cm = new Ext.grid.ColumnModel([
        { 
            id:'add',
            header: 'Add',
            renderer: render.enqColumn,
            sortable: false,
        },{
            id:'artist',
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
    ]);
    config.cm.defaultSortable = true;
    config.autoExpandColumn='artist';

    ArtistGrid.superclass.constructor.call(this, config);

    this.search = search;
    function search(text)
    {
        this.ds.filter('artist', text, true, false);
        return true;
    }
}
Ext.extend(ArtistGrid, BaseGrid);
