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
    player = new Player();
    playqueue = new PlayQueue('queue', 'songlist', fields);
    browser = new Browser(fields);
    settingspanel = new SettingsPanel();
    viewmgr = new ViewManager(bread_crumb.current_view(), {queue:playqueue});

    /* Initialize event handlers*/
    bread_crumb.on('bcupdate', viewmgr.set_panel, viewmgr);
    bread_crumb.on('newfilter', browser.load, browser);
    browser.on('newgrid', viewmgr.set_panel, viewmgr);
    browser.on('newgridbranch', add_grid_listeners);
    browser.on('newgridleaf', add_grid_leaf_listeners);
    browser.on('enqueue', playqueue.enqueue, playqueue);
    player.on('nextsong', playqueue.dequeue, playqueue);
    player.on('prevsong', playqueue.prev, playqueue);
    player.on('showprev', playqueue.showprev, playqueue);
    player.on('hideprev', playqueue.hideprev, playqueue);
    playqueue.on('playsong', player.playsong, player);
    playqueue.on('stop', player.stop, player);
}

function add_grid_listeners(crumb, e)
{
    crumb.panel.on("rowdblclick", bread_crumb.descend, bread_crumb);
}

function add_grid_leaf_listeners(crumb, e)
{
    crumb.panel.on("rowdblclick", player.playgridrow, player);
}

function enqueue(recordid)
{
    record = browser.ds.getById(recordid);
    playqueue.addRecord(record);
    Ext.EventObject.stopPropagation();
}

Ext.onReady(init);
/****End of Initializations ****/
