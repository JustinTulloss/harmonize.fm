YAHOO.example.Data = {
    bookorders: [
        {id:"po-0167", date:new Date(1980, 2, 24), quantity:1, amount:4, title:"A Book About Nothing"},
        {id:"po-0783", date:new Date("January 3, 1983"), quantity:null, amount:12.12345, title:"The Meaning of Life"},
        {id:"po-0297", date:new Date(1978, 11, 12), quantity:12, amount:1.25, title:"This Book Was Meant to Be Read Aloud"},
        {id:"po-1482", date:new Date("March 11, 1985"), quantity:6, amount:3.5, title:"Read Me Twice"}
    ]
}

YAHOO.util.Event.addListener(window, "load", function() {
    YAHOO.example.Basic = new function() {
        var myColumnDefs = [
            {key:"id", sortable:true, resizeable:true},
            {key:"date", formatter:YAHOO.widget.DataTable.formatDate, sortable:true, resizeable:true},
            {key:"quantity", formatter:YAHOO.widget.DataTable.formatNumber, sortable:true, resizeable:true},
            {key:"amount", formatter:YAHOO.widget.DataTable.formatCurrency, sortable:true, resizeable:true},
            {key:"title", sortable:true, resizeable:true}
        ];

        this.myDataSource = new YAHOO.util.DataSource(YAHOO.example.Data.bookorders);
        this.myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
        this.myDataSource.responseSchema = {
            fields: ["id","date","quantity","amount","title"]
        };

        this.myDataTable = new YAHOO.widget.DataTable("browser",
                myColumnDefs, this.myDataSource);
    };
});

