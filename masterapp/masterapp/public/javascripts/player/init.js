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
var errmgr = null;

/******* Initialization functions ********/
function init()
{
    bread_crumb = new BreadCrumb();
    player = new Player();
    playqueue = new PlayQueue();
    browser = new Browser();
    settingspanel = new SettingsPanel();
    viewmgr = new ViewManager(bread_crumb.current_view(), {queue:playqueue});
    errmgr = new ErrorManager();

    /* Initialize event handlers */
    bread_crumb.on('bcupdate', viewmgr.set_panel, viewmgr);
    bread_crumb.on('newfilter', browser.load, browser);

    browser.on('newgrid', viewmgr.set_panel, viewmgr);
    browser.on('newgrid', viewmgr.init_search, viewmgr);
    browser.on('chgstatus', viewmgr.set_status, viewmgr);
    browser.on('newgrid', add_grid_listeners);

    player.on('nextsong', playqueue.dequeue, playqueue);
    player.on('prevsong', playqueue.prev, playqueue);
    player.on('showprev', playqueue.showprev, playqueue);
    player.on('hideprev', playqueue.hideprev, playqueue);

    playqueue.on('playsong', player.playsong, player);
    playqueue.on('stop', player.stop, player);
}

function add_grid_listeners(crumb, e)
{
    crumb.panel.on('enqueue', playqueue.enqueue, playqueue);
    crumb.panel.on('chgstatus', viewmgr.set_status, viewmgr);
    if (typeinfo[crumb.type].next == 'play')
        crumb.panel.on("rowdblclick", playqueue.playgridrow, playqueue);
    else
        crumb.panel.on("rowdblclick", bread_crumb.descend, bread_crumb);
}

function enqueue(recordid)
{
    record = browser.ds.getById(recordid);
    playqueue.addRecord(record);
    Ext.EventObject.stopPropagation();
}

function enqueue_album(fid, aid, title, totaltracks, havesongs) {
	record = {data:{Friend_id:fid, type:'album', Album_id:aid,
					Album_title:title, Album_totaltracks:totaltracks,
					Album_havesongs:havesongs},
			  		get:(function(key) {return record.data[key];})};
	playqueue.enqueue([record])
}

Ext.onReady(init);
/****End of Initializations ****/
