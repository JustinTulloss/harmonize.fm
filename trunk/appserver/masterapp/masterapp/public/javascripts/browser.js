/* Justin Tulloss
 * 
 * JavaScript to handle the browser datatable
 */

function Browser()
{
    var myColumnDefs = [
    {key:"add", formatter:function(addCell) {
        addCell.innerHTML = '<img src="/images/enqueue.png" />';
        addCell.style.cursor = 'pointer';
        }, resizeable:false , width:"20px", label:"Add"},
    {key:"track_num", formatter:YAHOO.widget.DataTable.formatNumber, sortable:true, resizeable:true, label:"#", width:"15px"},
    {key:"title", sortable:true, resizeable:true, label:"Name"},
    {key:"artist", sortable:true, resizeable:true, label:"Artist"},
    {key:"album", sortable:true, resizeable:true, label:"Album"},
    {key:"year", formatter:YAHOO.widget.DataTable.formatNumber, sortable:true, resizeable:true, label:"Year", width:"50px"}
    ];

    this.dataSource= new YAHOO.util.DataSource(MockData.songs);
    this.dataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    this.dataSource.responseSchema = {
        fields: ["track_num", "title","artist","album","length","year"]
    };

    this.table = new YAHOO.widget.DataTable("browser",
                    myColumnDefs, this.dataSource);
    this.table.subscribe("rowMousedownEvent", makeDraggable);
    this.table.subscribe("rowClickEvent", this.table.onEventSelectRow);
    this.table.subscribe("rowSelectEvent", focusTable);

    function focusTable(oArgs)
    {
        this.table.focus();
    }

    function makeDraggable(oArgs)
    {
        var newDraggable = new YAHOO.util.DDProxy(oArgs.el, "songlist");
    }
}

/* Example Data *******************/
MockData = {
    songs: [
        {title:"15 Step", album:"In Rainbows", artist:"Radiohead", track_num:1, year:2007 },
        {title:"Bodysnatchers", album:"In Rainbows", artist:"Radiohead", track_num:2, year:2007 },
        {title:"Nude", album:"In Rainbows", artist:"Radiohead", track_num:3, year:2007 },
        {title:"Weird Fishes/Arpeggi", album:"In Rainbows", artist:"Radiohead", track_num:4, year:2007 },
        {title:"All I Need", album:"In Rainbows", artist:"Radiohead", track_num:5, year:2007 },
        {title:"Faust Arp", album:"In Rainbows", artist:"Radiohead", track_num:6, year:2007 },
    ]
}



