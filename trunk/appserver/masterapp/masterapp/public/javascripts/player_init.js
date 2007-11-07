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

/******* Initialization functions ********/
function init()
{
    bread_crumb = new BreadCrumb('breadcrumb');
    bread_crumb.update();
    flplayer = new Player('player');
    playqueue = new PlayQueue('queue', 'songlist');
    browser = new Browser('browser');
    browser.grid.on("rowdblclick", descend);
    init_seekbar();
    init_mouseovers();
    bigshow = new Ext.BorderLayout(document.body, {
        north: {
            initializeSize: 73,
            titlebar: false
        },
        west: {
            split: true,
            initialSize: '16%',
            titlebar:false,
            collapsible: true
        },
        center : {
        }
    });
    var CP = Ext.ContentPanel

    bigshow.beginUpdate();
    bigshow.add('north', new CP('header'));
    bigshow.add('west', new CP('queue', {title: 'Navigation', fitToFrame:true}));
    bigshow.add('center', new CP('browser', {fitToFrame:true}) );
    bigshow.endUpdate();
}

nextType = {artist:'album', album:'song', genre:'artist', friend:'artist'};
function descend(grid, rowIndex, e)
{
    ds = grid.getDataSource();
    record = ds.getAt(rowIndex);
    type = record.get("type");
    value = record.get(type);
    if (type == "song") {
        //tell player to play this song
        flplayer.sendEvent('playpause');
        return;
    }

    params = bread_crumb.descend(value, new BcEntry(nextType[type]));
    params["type"] = nextType[type];
    ds.load({params:params});
}

function go(type)
{
    bread_crumb.jump_to('home');
    bread_crumb.descend(null, new BcEntry(type));
    browser.ds.load({params:{type:type}});
}

function jump_to(type)
{
    params = bread_crumb.jump_to(type);
    params.type = type;
    browser.ds.load({params:params});
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

Ext.onReady(init);
/****End of Initializations ****/


function mouseGoesOver()
{
	this.src = mouseOvers[this.number].src;
}

function mouseGoesOut()
{
	this.src = mouseOuts[this.number].src;
}

