/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 */

function Browser(domObj, dropAction){
    
    var div = domObj

    this.dropAction = dropAction;

    // create the Data Store
    this.ds = new Ext.data.JsonStore({
        url:'player/get_data',
        root: 'data',
        fields: ['type', 'title', 'artist', 'album', 'year', 'genre', 'tracknumber', 'totaltracks', 'recs']
    });

    // the column model has information about grid columns
    // dataIndex maps the column to the specific data field in
    // the data store
    var cm = {
        songs:new Ext.grid.ColumnModel([
            {  id: 'add',
               header: 'Add',
               renderer: enqColumn,
               sortable: false,
               width: '20px'
            },{
               id: 'title', 
               header: "Title",
               dataIndex: 'title'
            },{
                id: 'like',
                header: "Liked",
                renderer: starColumn,
                sortable: true,
                width:'20px'
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
               renderer: recColumn
            }]),
        albums: new Ext.grid.ColumnModel([
            { id:'add',
              header: 'Add',
              renderer: enqColumn,
              sortable: false,
              width: '20px'
            },{
                id:'album',
                header: "Album",
                dataIndex: 'album'
            },{
                id: 'artist',
                header: "Artist",
                dataIndex: 'artist'
            },{
                id:'num_tracks',
                header: "Total Tracks",
                dataIndex: 'numtracks',
            }])};

    cm.defaultSortable=true;

    

    // create the editor grid
    this.grid = new Ext.grid.Grid(div, {
        ds: this.ds,
        cm: cm.songs,
        selModel: new Ext.grid.RowSelectionModel(),
        enableColLock:false,
        enableDragDrop: true,
        loadMask: true,
        autoSizeColumns: true,
        trackMouseOver: false
    });

    if (this.dropAction != null)
        this.grid.dragdrop = this.dropAction;

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
        return '<center><img src="/images/enqueue.png" /></center>';
    }

    function starColumn(value, p, record)
    {
        //figure out apacity from record.recs (or something like that)
        return '<center><img src="/images/star.png" /></center>';
    }

    function recColumn(value, p, record)
    {
        return '<center><img src="/images/recommend.png" /></center>';
    }

    /***** public functions ****/
    function changeColModel(type)
    {
        this.grid.reconfigure(ds, cm[type]);
    }
}
