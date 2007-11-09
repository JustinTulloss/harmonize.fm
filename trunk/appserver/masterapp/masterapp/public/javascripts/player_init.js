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
var bigshow = null;
var gridpanel = null;
var homepanel = null;
var bread_crumb = null;
var nextType = {artist:'album', album:'song', genre:'artist', friend:'artist'};
var fields = ['type', 'title', 'artist', 'album', 'year', 'genre', 
                  'tracknumber', 'totaltracks', 'totalalbums','recs', 
                  'albumlength', 'artistlength', 'numartists','numalbums',
                  'likesartists', 'exartists', 'numtracks', 'name', 'friend', 'songid', 'albumid'];

/******* Initialization functions ********/
function init()
{
    mousemgr = new MouseMgr();
    bread_crumb = new BreadCrumb('breadcrumb');
    bread_crumb.update();
    flplayer = new Player('player');
    playqueue = new PlayQueue('queue', 'songlist', fields);
    browser = new Browser('browser', fields);
    browser.grid.on("rowdblclick", descend);
    browser.ds.on("load", mousemgr.processImages, mousemgr);
    init_seekbar();

    gridpanel = new Ext.GridPanel(browser.grid, {title:"Browse", fitToFrame:true, closable:true, autocreate:true});
    homepanel = new Ext.ContentPanel('home', {title:"Home", fitToFrame:true, closable:true, autocreate:true});
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
            hideTabs: true
        }
    });
    var CP = Ext.ContentPanel

    bigshow.beginUpdate();
    bigshow.add('north', new CP('header'));
    bigshow.add('west', new CP('queue-container', {title: 'Navigation', fitToFrame:true}));
    bigshow.add('center', homepanel);
    bigshow.add('center', gridpanel);
    bigshow.getRegion('center').hidePanel(gridpanel);
    bigshow.getRegion('center').showPanel(homepanel);
    bigshow.endUpdate();

    /* Initialize event handlers*/
    playqueue.queue.on("add", songsqueued);
    Ext.get("nextbutton").on("click", playqueue.nextsong);
    Ext.get("prevbutton").on("click", playqueue.backsong);
    //Ext.get("prevbutton").on("mouseover", playqueue.showlast5);
}

function songsqueued(store, records, index)
{
    //this is the first stuff into the queue
    if (store.getCount()-records.length<=0) 
    {
        //flplayer.loadFile({file:'music/'+records[0].get('filename')});
        //flplayer.sendEvent('playpause');
    }
}

function descend(grid, rowIndex, e)
{
    var ds = grid.getDataSource();
    var record = ds.getAt(rowIndex);
    var type = record.get("type");
    var value = record.get(type);

    if (type == "song") {
        //tell player to play this song
        flplayer.sendEvent('playpause');
        return;
    }

    params = bread_crumb.descend(value, new BcEntry(nextType[type]));
    params["type"] = nextType[type];
    /*TODO: Get rid of this giant HACK! */
    if (type == 'album')
        params.artist = record.get('artist');

    ds.load({params:params});
    browser.changeColModel(nextType[type]);
}

function go(type)
{

    if (bread_crumb.current_view() != "home" && type == "home")
    {
        bigshow.beginUpdate();
        bigshow.getRegion('center').hidePanel(gridpanel);
        bigshow.getRegion('center').showPanel(homepanel);
        bigshow.endUpdate();
        bread_crumb.jump_to('home'); //this is not the below jump_to function
        return;
    }
    else if (bread_crumb.current_view() == "home" && type != "home")
    {
        bigshow.beginUpdate();
        bigshow.getRegion('center').hidePanel(homepanel);
        bigshow.getRegion('center').showPanel(gridpanel);
        bigshow.endUpdate();
    }
    else if (bread_crumb.current_view() == "home" && type == "home")
        return;

    bread_crumb.jump_to('home'); //this is not the below jump_to function
    bread_crumb.descend(null, new BcEntry(type));
    browser.ds.load({params:{type:type}});
    browser.changeColModel(type);
    return;

}

function jump_to(type)
{
    if (type == 'home' && bread_crumb.current_view()!='home') {
        bigshow.beginUpdate();
        bigshow.getRegion('center').hidePanel(gridpanel);
        bigshow.getRegion('center').showPanel(homepanel);
        bigshow.endUpdate();
        params = bread_crumb.jump_to(type);
        return;
    }
    else if (type != 'home' && bread_crumb.current_view() == 'home') {
        bigshow.beginUpdate();
        bigshow.getRegion('center').hidePanel(homepanel);
        bigshow.getRegion('center').showPanel(gridpanel);
        bigshow.endUpdate();
    }

    params = bread_crumb.jump_to(type);
    params.type = type;
    browser.ds.load({params:params});
    browser.changeColModel(type);
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

