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
var friend_radio = null;
var playlistmgr = null;

/******* Initialization functions ********/
function init()
{
    bread_crumb = new BreadCrumb();
    player = new Player();
	playlistmgr = new PlaylistMgr();
	playqueue = playlistmgr.playqueue;
    browser = new Browser();
    settingspanel = new SettingsPanel();
    viewmgr = new ViewManager(bread_crumb.current_view(), {queue:playlistmgr});
    errmgr = new ErrorManager();
    friend_radio = new FriendRadio();

    /* Initialize event handlers */
    bread_crumb.on('bcupdate', viewmgr.set_panel, viewmgr);
    bread_crumb.on('newfilter', browser.load, browser);
    bread_crumb.on('chgstatus', viewmgr.set_status, viewmgr);

    browser.on('newgrid', viewmgr.set_panel, viewmgr);
    browser.on('newgrid', viewmgr.init_search, viewmgr);
    browser.on('chgstatus', viewmgr.set_status, viewmgr);
    browser.on('newgrid', add_grid_listeners);

    player.on('nextsong', playqueue.dequeue);
    player.on('prevsong', playqueue.prev);
    player.on('showprev', playqueue.showprev);
    player.on('hideprev', playqueue.hideprev);

    playqueue.on('playsong', player.playsong);
    playqueue.on('stop', player.stop);
	playqueue.on('buffersong', player.buffersong);
	
	Ext.get("friend_radio_link").on('click', friend_radio.toggle, friend_radio);

    urlm.register_action('invite', invite_friend);

	function jump_bc(rest) {
		bread_crumb.go(rest);
	}

    urlm.init([
        ['/bc/', urlm.ignore_matched(bread_crumb.load_url)],
		['/people/profile/\\d+', urlm.handle_matched(profile_handler)]
        /*['/profile/', urlm.generate_panel(profile_factory)]*/
    ]);
	init_feedback();
    /* Handles login excpetions universally */
    Ext.Ajax.on('requestexception', function(conn, response, options) {
        if (response.status == 401){
            alert(['Your login has expired.\n\n',
                'You will now be directed to a facebook login page. ',
                'After you login, you be directed back to harmonize.fm'].join('')
            );
            var href = global_config.fblogin_url+
                '&next='+location.pathname+location.hash;
            location.href= href;
        }
    });
}

function add_grid_listeners(crumb, e)
{
	function record_handler(handler) {
		return function(grid, songindex, e) {
			return handler(grid.store.getAt(songindex));
		};
	}
    crumb.panel.on('enqueue', playlistmgr.enqueue);
    crumb.panel.on('chgstatus', viewmgr.set_status, viewmgr);
    if (typeinfo[crumb.type].next == 'play')
        crumb.panel.on("rowdblclick", playqueue.playgridrow, playqueue);
	else if (typeinfo[crumb.type].next == 'openplaylist')
		crumb.panel.on('rowdblclick',record_handler(playlist_dblclick));
    else
        crumb.panel.on("rowdblclick", bread_crumb.descend, bread_crumb);
}

function enqueue(recordid)
{
    record = browser.ds.getById(recordid);
    playqueue.addRecord(record);
    Ext.EventObject.stopPropagation();
}

function enqueue_spotlight(id, friendid, type) {
    if (type == "playlist") enqueue_playlist(id, friendid);
    else enqueue_album(id, friendid);
}
/* enqueue_album is only used for spotlight albums
 */
function enqueue_album(albumid, friendid) {
	function enqueue_result(response) {
		var record = untyped_record(response);
		record.set('Friend_id',  friendid);
        record.set('source', 2); //from a spotlight
		playlistmgr.enqueue([record]);
	}
	Ext.Ajax.request({
		url:'/metadata/album/'+albumid,
		success: enqueue_result,
        params: {friend: friendid}
    });
}

/* enqueue_playlist is only used for playlist spotlights
 */
function enqueue_playlist(playlistid, friendid) {
	function enqueue_result(response) {
		var record = untyped_record(response);
		record.set('Friend_id',  friendid);
        record.set('source',2); // from a spotlight
		playlistmgr.enqueue([record]);
	}
	Ext.Ajax.request({
		url:'/metadata/playlist/'+playlistid,
		success: enqueue_result,
        params: {friend: friendid}
    });
}

Ext.onReady(init);
/****End of Initializations ****/
