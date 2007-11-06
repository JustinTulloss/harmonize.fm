/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *  --Largely based off browser class for now
 *
 *  Updated 11/6/07 (r43) to support ExtJS --JMT
 */

function PlayQueue(domObj, dragGroup)
{
    this.div = domObj;
    var queue = new Ext.dd.DropTarget(this.div);
    queue.addToGroup("GridDD"); //This is undocumented, but necessary!

    var colDefs= [
    {key:"song_expand", formatter:function(addCell) {
        addCell.innerHTML = '<img src="/images/song_expand.png" />';
        addCell.style.cursor = 'pointer';
        }, resizeable:false , width:"15px"},
    {key:"title"},
    {key:"song_remove", formatter:function(addCell) {
        addCell.innerHTML = '<img src="/images/song_remove.png" />';
        addCell.style.cursor = 'pointer';
        }, resizeable:false , width:"15px"},
    ];

    this.dataSource= new YAHOO.util.DataSource();
    this.dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
    this.dataSource.responseSchema = {
        fields: ["track_num", "title","artist","album","length","year"]
    };
    
    this.table = null;

    queue.notifyDrop = dropAction;

    function dropAction(source, e, data)
    {
        data.selections.each(addSelection);
    }

    function addSelection(song) {
        addRow(song.data);
    }
    
    /* Public functions */
    this.addRow = addRow;

    function addRow(newRow)
    {
        if (this.table == null) 
            this.table = new YAHOO.widget.DataTable(this.div,
                    colDefs, this.dataSource);
        this.table.addRow(newRow);
    }

}


