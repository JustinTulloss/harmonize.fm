/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 */

function Browser(domObj){
    
    var div = domObj
    // create the Data Store
    var ds = new Ext.data.JsonStore({
        url:'player/get_songs',
        root: 'data',
        fields: ['title', 'artist', 'album']
    });

    // pluggable renders
    function renderTopic(value, p, record){
        return String.format('<b>{0}</b>{1}', value, record.data['excerpt']);
    }
    function renderTopicPlain(value){
        return String.format('<b><i>{0}</i></b>', value);
    }
    function renderLast(value, p, r){
        //return String.format('{0}<br/>by {1}', value.dateFormat('M j, Y, g:i a'), r.data['author']);
        return null;
    }
    function renderLastPlain(value){
        return value.dateFormat('M j, Y, g:i a');
    }

    // the column model has information about grid columns
    // dataIndex maps the column to the specific data field in
    // the data store
    var cm = new Ext.grid.ColumnModel([{
           id: 'topic', // id assigned so we can apply custom css (e.g. .x-grid-col-topic b { color:#333 })
           header: "Topic",
           dataIndex: 'title',
           width: 490,
           //renderer: renderTopic,
           css: 'white-space:normal;'
        },{
           header: "Author",
           dataIndex: 'album',
           width: 100
           //hidden: true
        },{
           id: 'last',
           header: "Last Post",
           dataIndex: 'artist',
           width: 150
           //renderer: renderLast
        }]);

    

    // create the editor grid
    var grid = new Ext.grid.Grid(div, {
        ds: ds,
        cm: cm,
        selModel: new Ext.grid.RowSelectionModel(),
        enableColLock:false,
        loadMask: true
    });

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

    var gridFoot = grid.getView().getFooterPanel(true);

    // add a paging toolbar to the grid's footer
    var paging = new Ext.PagingToolbar(gridFoot, ds, {
        pageSize: 25,
        displayInfo: true,
        displayMsg: 'Displaying topics {0} - {1} of {2}',
        emptyMsg: "No topics to display"
    });
    // add the detailed view button
    paging.add('-', {
        pressed: true,
        enableToggle:true,
        text: 'Detailed View',
        cls: 'x-btn-text-icon details',
        toggleHandler: toggleDetails
    });

    // trigger the data store load
    //ds.load({params:{start:0, limit:25}});
    ds.load();

    function toggleDetails(btn, pressed){
        cm.getColumnById('topic').renderer = pressed ? renderTopic : renderTopicPlain;
        cm.getColumnById('last').renderer = pressed ? renderLast : renderLastPlain;
        grid.getView().refresh();
    }
}

