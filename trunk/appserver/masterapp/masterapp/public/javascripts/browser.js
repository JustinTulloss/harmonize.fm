/* Justin Tulloss
 * 
 * JavaScript to handle the browser datatable
 */

function Browser()
{
    var YDT = YAHOO.widget.DataTable;

    /*TODO: Make the CSS center the controls, not the <center> tag */
    var columnDefs ={
    song: [
        {key:"add", formatter:function(addCell) {
            addCell.innerHTML = '<center><img src="/images/enqueue.png" /></center>';
            addCell.style.cursor = 'pointer';
            }, resizeable:false , width:"20px", label:"Add"},
        {key:"track_num", formatter:YDT.formatNumber, sortable:true, resizeable:true, label:"#", width:"15px"},
        {key:"title", sortable:true, resizeable:true, label:"Name"},
        {key:"liked", sortable:true, resizeable:true, label:"Liked", formatter:function(starCell){
            starCell.innerHTML='<center><img src="/images/star.png" /></center>';
            }, width:"15px"},
        {key:"artist", sortable:true, resizeable:true, label:"Artist"},
        {key:"album", sortable:true, resizeable:true, label:"Album"},
        {key:"year", formatter:YDT.formatNumber, sortable:true, resizeable:true, label:"Year", width:"50px"},
        {key:"rec", formatter:function(recCell){
            recCell.innerHTML = '<center><img src="/images/recommend.png" /></center>';
            recCell.style.cursor = 'pointer';
            }, resizeable:false, width:"20px", label:"Recommend", sortable:false},
        {key:"menu", formatter:function(recCell){
            recCell.innerHTML = '<center><img src="/images/menu.png" /></center>';
            recCell.style.cursor = 'pointer';
            }, resizeable:false, sortable:false, label:"Other", width:"20px"}
        ],
    album: [
        {key:"add", formatter:function(addCell) {
            addCell.innerHTML = '<center><img src="/images/enqueue.png" /></center>';
            addCell.style.cursor = 'pointer';
            }, resizeable:false , width:"20px", label:"Add"},
        {key:"album", sortable:true, resizeable:true, label:"Album"},
        {key:"liked", sortable:true, resizeable:true, label:"Liked", formatter:function(starCell){
            starCell.innerHTML='<center><img src="/images/star.png" /></center>';
            }, width:"15px"},
        {key:"artist", sortable:true, resizeable:true, label:"Artist"},
        {key:"year", formatter:YDT.formatNumber, sortable:true, resizeable:true, label:"Year", width:"50px"},
        {key:"rec", formatter:function(recCell){
            recCell.innerHTML = '<center><img src="/images/recommend.png" /></center>';
            recCell.style.cursor = 'pointer';
            }, resizeable:false, width:"20px", label:"Recommend", sortable:false},
        {key:"menu", formatter:function(recCell){
            recCell.innerHTML = '<center><img src="/images/menu.png" /></center>';
            recCell.style.cursor = 'pointer';
            }, resizeable:false, sortable:false, label:"Other", width:"20px"}
        ],
    };

    this.dataSource= new YAHOO.util.DataSource(MockData.albums);
    this.dataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    this.dataSource.responseSchema = {
        fields: ["track_num", "title","artist","album","length","year"]
    };

    this.table = new YAHOO.widget.DataTable("browser",
                    columnDefs['album'], this.dataSource);
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
    ],
    albums: [
        {album:"Amnesiac", year: "2001", artist:"Radiohead", tracks:11},
        {album:"B-Sides", artist:"Radiohead" },
        {album:"The Bends", year: "1995", artist:"Radiohead", tracks:12},
        {album:"Hail to the Thief", year: "2003", artist:"Radiohead", tracks:14},
        {album:"In Rainbows", year: "2007", artist:"Radiohead", tracks:10},
        {album:"Kid A", artist:"Radiohead", tracks:10},
        {album:"OK Computer", year: "1997", artist:"Radiohead", tracks:12}
    ]
}



