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
        {key:"tracknumber", formatter:YDT.formatNumber, sortable:true, resizeable:true, label:"#", width:"15px"},
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
    
    this.dataSource = new YAHOO.util.DataSource("/player/get_songs");  
    this.dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
    //this.myDataSource.connXhrMode = "queueRequests"; 
    this.dataSource.responseSchema = {
        resultsList: "data",
        fields: ["artist", "album", "title", "tracknumber", "year", "recs", "genre", "totaltracks"]
    };

    this.table = new YAHOO.widget.DataTable("browser",
                                   columnDefs["song"], this.dataSource);
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
