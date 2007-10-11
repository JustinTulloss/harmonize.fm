/* Get Window height and width **********/
var winW = 630, winH = 460;

if (parseInt(navigator.appVersion)>3) {
    if (navigator.appName.indexOf("Microsoft")!=-1) {
        winW = document.body.offsetWidth;
        winH = document.body.offsetHeight;
    }
    else {
        winW = window.innerWidth;
        winH = window.innerHeight;
    }
}

/* Initialize Flash Player **************/

function embed_player()
{
    var so = new SWFObject('/flash/mediaplayer.swf','rubiconfl','0','0','7');
    so.addParam('allowfullscreen','true');
    so.addVariable('file','music/a12883770c0e5760744b24110af1b45ef7083f7b');
    so.addVariable('showdigits','false');
    so.addVariable('shuffle','false');
    so.addVariable('smoothing','false');
    so.addVariable('enablejs','true');
    so.addVariable('javascriptid','rubiconfl');
    so.addVariable('type','mp3');
    so.addVariable('usecaptions','false');
    so.addVariable('usefullscreen','false');
    so.write('player');
}

// some variables to save
var currentPosition;
var currentVolume;
var currentItem;

// these functions are caught by the JavascriptView object of the player.
function sendEvent(typ,prm) { thisMovie("rubiconfl").sendEvent(typ,prm); };
function getUpdate(typ,pr1,pr2,pid) {
    if(typ == "time") { currentPosition = pr1; }
    else if(typ == "volume") { currentVolume = pr1; }
    var id = document.getElementById(typ);
    var id2 = document.getElementById(typ + '2');
    id.innerHTML = Math.round(pr1);
    pr2 == undefined ? null: id2.innerHTML = Math.round(pr2);
};

// These functions are caught by the feeder object of the player.
function loadFile(obj) { thisMovie("rubiconfl").loadFile(obj); };
function addItem(obj,idx) { thisMovie("rubiconfl").addItem(obj,idx); }
function removeItem(idx) { thisMovie("rubiconfl").removeItem(idx); }

// This is a javascript handler for the player and is always needed.
function thisMovie(movieName) {
    if(navigator.appName.indexOf("Microsoft") != -1) {
        return window[movieName];
    } else {
        return document[movieName];
    }
};


/* Yahoo Example Data *******************/
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
    embed_player();
});

