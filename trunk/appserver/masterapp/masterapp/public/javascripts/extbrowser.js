/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 */

function Browser(domObj, dropAction){
    
    var div = domObj

    this.dropAction = dropAction;

    // create the Data Store
    var ds = new Ext.data.JsonStore({
        url:'player/get_songs',
        root: 'data',
        fields: ['title', 'artist', 'album']
    });

    // the column model has information about grid columns
    // dataIndex maps the column to the specific data field in
    // the data store
    var cm = new Ext.grid.ColumnModel([{
           id: 'title', 
           header: "Title",
           dataIndex: 'title'
        },{
           id: 'album',
           header: "Album",
           dataIndex: 'album'
        },{
           id: 'artist',
           header: "Artist",
           dataIndex: 'artist'
        }]);

    cm.defaultSortable=true;

    

    // create the editor grid
    var grid = new Ext.grid.Grid(div, {
        ds: ds,
        cm: cm,
        selModel: new Ext.grid.RowSelectionModel(),
        enableColLock:false,
        enableDragDrop: true,
        loadMask: true,
        autoSizeColumns: true,
        trackMouseOver: false
    });

    if (this.dropAction != null)
        grid.dragdrop = this.dropAction;

    // make the grid resizable, do before render for better performance
    var rz = new Ext.Resizable(div, {
        wrap:true,
        minHeight:100,
        pinned:true,
        handles: 's'
    });
    rz.on('resize', grid.autoSize, grid);

    // render it
    grid.render();

    // trigger the data store load
    ds.load();
}

