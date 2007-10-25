/* Initialize Flash Player **************/

function embed_player()
{
    var so = new SWFObject('/flash/mediaplayer.swf','rubiconfl','0','0','7');
    so.useExpressInstall('/flash/expressinstall.swf')
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
var totalTime;

// these functions are caught by the JavascriptView object of the player.
function sendEvent(typ,prm) { thisMovie("rubiconfl").sendEvent(typ,prm); };

//TODO: Make this function less ugly than sin
function getUpdate(typ,pr1,pr2,pid) {
    if(typ == "time") { currentPosition = pr1; }
    else if(typ == "volume") { currentVolume = pr1; }
    var id = document.getElementById(typ);
    var id2 = document.getElementById(typ + '2');
    mins = Math.round(pr1/60)
    secs = Math.round(pr1%60)
    id.innerHTML = leadingZero(mins) + ":" + leadingZero(secs)
    mins = Math.round(pr2/60)
    secs = Math.round(pr2%60)
    pr2 == undefined ? null: id2.innerHTML = "-"+leadingZero(mins)+":"+leadingZero(secs)
    if (typ == "time") {
        totalTime = pr1 + pr2;
        spos = 100*pr1/totalTime
        YAHOO.util.Dom.setStyle('shuttle', 'left', String(spos)+"px");
    }
};

function leadingZero(nr) {
    if (nr < 10)
        nr = "0" + nr;
    return nr;
}

// These functions are caught by the feeder object of the player.
function loadFile(obj) { thisMovie('rubiconfl').loadFile(obj); };
function addItem(obj,idx) { thisMovie('rubiconfl').addItem(obj,idx); }
function removeItem(idx) { thisMovie('rubiconfl').removeItem(idx); }

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

/****
* drag and drop test
*I'll probably mess this up pretty good
****/
var row0 = new YAHOO.util.DDProxy("yui-dt0-bdrow0", "songlist");
var row1 = new YAHOO.util.DDProxy("yui-dt0-bdrow1", "songlist");
var row2 = new YAHOO.util.DDProxy("yui-dt0-bdrow2", "songlist");
var row3 = new YAHOO.util.DDProxy("yui-dt0-bdrow3", "songlist");
var queue = new YAHOO.util.DDTarget("queue");
var browser = new YAHOO.util.DDTarget("browser");

/****
*  somehow make it so the queue can accept dropped items
* and display them in a reasonable manner
****/



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


/**** Sets up the slider for the flash player
 * I'm not really sure why it's in it's own generic function,
 * but that's how the example player was.
 ********/
(function() {
    var Event = YAHOO.util.Event,
        Dom   = YAHOO.util.Dom,
        lang  = YAHOO.lang,
        slider, 
        bg="timeline", thumb="shuttle", 
        valuearea="slider-value", textfield="slider-converted-value"

    // The slider can move 0 pixels up
    var topConstraint = 0;

    // The slider can move 100 pixels
    var bottomConstraint = 100;

    // Custom scale factor for converting the pixel offset into a real value
    var scaleFactor = 1;

    Event.onDOMReady(function() {

        slider = YAHOO.widget.Slider.getHorizSlider(bg, 
                         thumb, topConstraint, bottomConstraint, 1);

        slider.getRealValue = function() {
            return Math.round(this.getValue() * scaleFactor);
        }

        slider.subscribe("change", function(offsetFromStart) {
            
            //figure out how much we changed
            //send that change to the player
            sendEvent('scrub', totalTime*offsetFromStart/100)
            // Update the title attribute on the background.  This helps assistive
            // technology to communicate the state change
            Dom.get(bg).title = "slider value = " + actualValue;

        });

        slider.subscribe("slideStart", function() {
                YAHOO.log("slideStart fired", "warn");
            });

        slider.subscribe("slideEnd", function() {
                YAHOO.log("slideEnd fired", "warn");
            });

        // Listen for keystrokes on the form field that displays the
        // control's value.  While not provided by default, having a
        // form field with the slider is a good way to help keep your
        // application accessible.
        Event.on(textfield, "keydown", function(e) {

            // set the value when the 'return' key is detected
            if (Event.getCharCode(e) === 13) {
                var v = parseFloat(this.value, 10);
                v = (lang.isNumber(v)) ? v : 0;

                // convert the real value into a pixel offset
                slider.setValue(Math.round(v/scaleFactor));
            }
        });
        
        // Use setValue to reset the value to white:
        Event.on("putval", "click", function(e) {
            slider.setValue(100, false); //false here means to animate if possible
        });
        
        // Use the "get" method to get the current offset from the slider's start
        // position in pixels.  By applying the scale factor, we can translate this
        // into a "real value
        Event.on("getval", "click", function(e) {
            YAHOO.log("Current value: "   + slider.getValue() + "\n" + 
                      "Converted value: " + slider.getRealValue(), "info", "example"); 
        });
    });
})();

