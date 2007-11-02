/* Initialize Everything**************/

/*** Initially put together by Justin Tulloss 
 *
 * History:
 * 10/24/2007 - Cleaned this up a lot --JMT
 * 10/31/2007 - Moved classes to their own files --JMT
 */

/*Globals to make the YUI library easier to access */
var Event = YAHOO.util.Event,
    Dom   = YAHOO.util.Dom,
    lang  = YAHOO.lang;

/* Other necessary globals. Any globals outside of here 
 * should be removed at some point, or determined as necessary
 * and put here
 */

var flplayer; //the flash player
var playqueue = null;
var browser = null;
var bread_crumb = null;

/****
* drag and drop test
*I'll probably mess this up pretty good
****/
var row0 = new YAHOO.util.DDProxy("yui-dt0-bdrow0", "songlist");
/*
var row1 = new YAHOO.util.DDProxy("yui-dt0-bdrow1", "songlist");
var row2 = new YAHOO.util.DDProxy("yui-dt0-bdrow2", "songlist");
var row3 = new YAHOO.util.DDProxy("yui-dt0-bdrow3", "songlist");
*/

row0.onDragDrop = function(e, id)
{
    if (id=="queue"){
        enqueueRow(this.id);
    }
    
};

function enqueueRow(rowId)
{
    newRecord = browser.table.getRecord(rowId);
    playqueue.addRow(newRecord._oData); //This is a horrible abuse of "private" data
}


/******* Initialization functions ********/
function init()
{
    bread_crumb = new BreadCrumb('breadcrumb');
    flplayer = new Player('player');
    browser = new Browser();
    browser.table.subscribe("rowDblclickEvent", descend);
    playqueue = new PlayQueue('queue', 'songlist');
    init_seekbar();
    init_mouseovers();
}

function descend(oArgs)
{
    alert(bread_crumb.descend(new BcEntry("album", "In Rainbows")));
}

/***TODO: Get rid of this slop******/
var slider, 
bg="timeline", thumb="shuttle", 
valuearea="slider-value", textfield="slider-converted-value"

// The slider can move 0 pixels up
var topConstraint = 0;

// The slider can move 100 pixels
var bottomConstraint = 100;

// Custom scale factor for converting the pixel offset into a real value
var scaleFactor = 1;

function init_seekbar()
{
    slider = YAHOO.widget.Slider.getHorizSlider(bg, 
            thumb, topConstraint, bottomConstraint, 1);

    slider.getRealValue = function() {
        return Math.round(this.getValue() * scaleFactor);
    }

    slider.subscribe("change", function(offsetFromStart) {

            //figure out how much we changed
            //send that change to the player
            flplayer.seek(offsetFromStart/100);
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
}

/* Mouseover code that doesn't require mouseover being in the HTML 
 * Blatantly stolen with much thanks from 
 * http://www.quirksmode.org/js/mouseov.html 
 */
var W3CDOM = (document.createElement && document.getElementsByTagName);

var mouseOvers = new Array();
var mouseOuts = new Array();
var playpause = new Array();

function init_mouseovers()
{
	if (!W3CDOM) return;
	var nav = document.getElementById('controls');
	var imgs = nav.getElementsByTagName('img');
	for (var i=0;i<imgs.length;i++)
	{
		imgs[i].onmouseover = mouseGoesOver;
		imgs[i].onmouseout = mouseGoesOut;
		var suffix = imgs[i].src.substring(imgs[i].src.lastIndexOf('.'));
		mouseOuts[i] = new Image();
		mouseOuts[i].src = imgs[i].src;
		mouseOvers[i] = new Image();
		mouseOvers[i].src = imgs[i].src.substring(0,imgs[i].src.lastIndexOf('.')) + "_over" + suffix;
		imgs[i].number = i;
	}
}

Event.onDOMReady(init);
/****End of Initializations ****/


function mouseGoesOver()
{
	this.src = mouseOvers[this.number].src;
}

function mouseGoesOut()
{
	this.src = mouseOuts[this.number].src;
}

