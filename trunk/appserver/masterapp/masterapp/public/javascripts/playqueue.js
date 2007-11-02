/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *  --Largely based off browser class for now
 */

function PlayQueue(domObj, dragGroup)
{
    var queue = new YAHOO.util.DDTarget(domObj, dragGroup);

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
    this.dataSource.responseType = YAHOO.util.DataSource.TYPE_UNKNOWN;
    this.dataSource.responseSchema = {
        fields: ["track_num", "title","artist","album","length","year"]
    };
    
    this.table = null;
    
    /* Public functions */
    this.addRow = addRow;

    function addRow(newRow)
    {
        if (this.table == null) 
            this.table = new YAHOO.widget.DataTable(domObj,
                    colDefs, this.dataSource);
        this.table.addRow(newRow);
    }

}


