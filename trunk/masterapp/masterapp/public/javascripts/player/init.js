/*** Initially put together by Justin Tulloss 
 *
 * History:
 * 10/24/2007 - Cleaned this up a lot --JMT
 * 10/31/2007 - Moved classes to their own files --JMT
 * 03/03/2008 - Starting on a cleanup. Hoping to put as much as possible in
 *              event handlers not found here. --JMT
 */

Ext.BLANK_IMAGE_URL='/images/s.gif';

/* Other necessary globals. Any globals outside of here 
 * should be removed at some point, or determined as necessary
 * and put here
 */

var player = null;
var playqueue = null;
var browser = null;
var viewmgr = null;
var bread_crumb = null;
var settingspanel = null;

/******* Initialization functions ********/
function init()
{
    bread_crumb = new BreadCrumb();
    player = new Player('player');
    playqueue = new PlayQueue('queue', 'songlist', fields);
    browser = new Browser(fields);
    settingspanel = new SettingsPanel();
    viewmgr = new ViewManager(bread_crumb.current_view(), {queue:playqueue});
    init_seekbar();

    /* Initialize event handlers*/
    bread_crumb.on('bcupdate', viewmgr.set_panel, viewmgr);
    bread_crumb.on('newfilter', browser.load, browser);
    browser.on('newgrid', viewmgr.set_panel, viewmgr);
    browser.on('newgrid', add_grid_listeners);
    Ext.get("nextbutton").on("click", playqueue.nextsong, playqueue);
    Ext.get("prevbutton").on("click", playqueue.backsong, playqueue);
}

function add_grid_listeners(crumb, e)
{
    crumb.panel.on("rowdblclick", bread_crumb.descend, bread_crumb);
}

function enqueue(recordid)
{
    record = browser.ds.getById(recordid);
    playqueue.addRecord(record);
    Ext.EventObject.stopPropagation();
}

function descend(grid, rowIndex, e)
{
    var record = grid.getStore().getAt(rowIndex);
    var type = record.get("type");
    var value = record.get(type);
    var nexttype = typeinfo[type]['next'];

    if (nexttype == 'play') {
        //tell player to play this song
        player.playsong(record);
        return;
    }

    var newbc =  new BcEntry(nexttype);
    if (typeinfo[nexttype] != null) {
        if (typeinfo[nexttype]['qry'] != null) {
            newbc.qrytype = typeinfo[nexttype]['qry'];
        }
    }

    qryvalue = value;
    if (typeinfo[type]['qry'] != null)
        qryvalue = record.get(typeinfo[type]['qry']);

    var params = bread_crumb.descend(value, qryvalue, newbc);
    params["type"] = nexttype;
    grid.getStore().load({params:params});
    browser.changeColModel(nexttype);
}

var slider, 
bg="timeline", thumb="shuttle" 

function init_seekbar()
{
    slider = new Ext.ux.SlideZone('timeline', {
        type: 'horizontal',
        size:100,
        sliderWidth: 13,
        //sliderHeight: 13,
        maxValue: 100,
        minValue: 0,
        sliderSnap: 1,
        sliders: [{
            value: 0,
            name: 'shuttle'
        }]
    });

    slider.getSlider('shuttle').on('drag',
        function() {
            player.seek(this.value/100)
        });
}

Ext.onReady(init);
/****End of Initializations ****/
