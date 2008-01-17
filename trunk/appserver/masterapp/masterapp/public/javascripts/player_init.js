/* Initialize Everything**************/

/*** Initially put together by Justin Tulloss 
 *
 * History:
 * 10/24/2007 - Cleaned this up a lot --JMT
 * 10/31/2007 - Moved classes to their own files --JMT
 */

Ext.BLANK_IMAGE_URL='/images/s.gif';

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
var typeinfo= {
    artist:{next:'album'}, 
    album:{next:'song', qry:'album_id'}, 
    genre:{next:'artist'},
    friend:{next:'artist', qry:'fid'}
};
var fields = ['type', 'title', 'artist', 'album', 'year', 'genre', 
                  'tracknumber', 'totaltracks', 'totalalbums','recs', 
                  'albumlength', 'artistlength', 'numartists','numalbums',
                  'likesartists', 'exartists', 'numtracks', 'name', 'friend', 
                  'songid', 'album_id', 'filename'];

/******* Initialization functions ********/
function init()
{
    mousemgr = new MouseMgr();
    bread_crumb = new BreadCrumb('breadcrumb');
    bread_crumb.update();
    flplayer = new Player('player');
    playqueue = new PlayQueue('queue', 'songlist', fields);
    browser = new Browser(fields);
    init_seekbar();
    init_top_menu();

    homepanel = new Ext.Panel({title:"Home", fitToFrame:true, closable:true, autocreate:true, contentEl:'home', header: false});

    bigshow = new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            height: 76,
            titlebar: false,
            contentEl: 'header'
        },{
            region: 'west',
            split: true,
            width: '16%',
            titlebar:false,
            collapsible: true,
            items: [playqueue.tree]
        }, {
            region: 'center',
            id: 'centerpanel',
            layout: 'card',
            activeItem: 0,
            items: [homepanel, browser.grid]
        }]
    });
    var CP = Ext.ContentPanel

    /* Initialize event handlers*/
    //playqueue.queue.on("add", songsqueued);
    browser.grid.on("rowdblclick", descend);
    browser.ds.on("load", mousemgr.processImages, mousemgr);
    Ext.get("nextbutton").on("click", playqueue.nextsong,playqueue);
    Ext.get("prevbutton").on("click", playqueue.backsong, playqueue);
    playqueue.on("playsong", playnewsong);
    //Ext.get("prevbutton").on("mouseover", playqueue.showlast5);
}

function enqueue(recordid)
{
    record = browser.ds.getById(recordid);
    playqueue.addRecord(record);
    Ext.EventObject.stopPropagation();
}

function playnewsong(song)
{
    flplayer.loadFile({file:'music/'+song.get('filename')});
    flplayer.sendEvent('playpause');
}

function descend(grid, rowIndex, e)
{
    var ds = grid.getStore();
    var record = ds.getAt(rowIndex);
    var type = record.get("type");
    var value = record.get(type);

    if (type == "song") {
        //tell player to play this song
        flplayer.loadFile({file:'music/'+escape(record.get('filename'))});
        flplayer.sendEvent('playpause');
        playqueue.setNowPlaying(record);
        return;
    }

    var nexttype = typeinfo[type]['next'];
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

    ds.load({params:params});
    browser.changeColModel(nexttype);
}

function go(type)
{

    if (bread_crumb.current_view() != "home" && type == "home")
    {
        bigshow.getComponent('centerpanel').getLayout().setActiveItem(0);
        bread_crumb.jump_to('home'); //this is not the below jump_to function
        return;
    }
    else if (bread_crumb.current_view() == "home" && type != "home")
    {
        bigshow.getComponent('centerpanel').getLayout().setActiveItem(1);
    }
    else if (bread_crumb.current_view() == "home" && type == "home")
        return;

    bread_crumb.jump_to('home'); //this is not the below jump_to function
    bread_crumb.descend(null, null, new BcEntry(type));
    browser.ds.load({params:{type:type}});
    browser.changeColModel(type);
    return;

}

function jump_to(type)
{
    if (type == 'home' && bread_crumb.current_view()!='home') {
        bigshow.getComponent('centerpanel').getLayout().setActiveItem(0);
        params = bread_crumb.jump_to(type);
        return;
    }
    else if (type != 'home' && bread_crumb.current_view() == 'home') {
        bigshow.getComponent('centerpanel').getLayout().setActiveItem(1);
    }

    params = bread_crumb.jump_to(type);
    params.type = type;
    browser.ds.load({params:params});
    browser.changeColModel(type);
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
            flplayer.seek(this.value/100)
        });
}

function init_top_menu()
{
    topmenu = new Ext.Toolbar({renderTo: 'menu', cls:'menu', height:18});
    var homebtn = new Ext.Toolbar.Button({text:'Home', cls:'menuitem'});
    var artistbtn= new Ext.Toolbar.Button({text:'Artists', cls:'menuitem'});
    var albumbtn= new Ext.Toolbar.Button({text:'Albums', cls:'menuitem'});
    var songsbtn= new Ext.Toolbar.Button({text:'Songs', cls:'menuitem'});
    var friendsbtn= new Ext.Toolbar.Button({text:'Friends', cls:'menuitem'});
    var genresbtn= new Ext.Toolbar.Button({text:'Genres', cls:'menuitem'});
    var settingsbtn= new Ext.Toolbar.Button({text:'Settings', cls:'menuitem'});
    homebtn.on('click', go);
    artistbtn.on('click', go);
    albumbtn.on('click', go);
    songsbtn.on('click', go);
    friendsbtn.on('click', go);
    genresbtn.on('click', go);
    settingsbtn.on('click', showSettings);

    topmenu.add(homebtn,artistbtn,albumbtn,songsbtn,friendsbtn,genresbtn,settingsbtn);
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
	
function showSettings(){
	// create the window on the first click and reuse on subsequent clicks
	var win;
	if(!win){
		win = new Ext.Window({
			width:500,
			height:300,
			closeAction:'hide',
			autoScroll:'true',
			html:showFriends,
			layout:'accordion',
			buttons: [{
				text:'Save',
				handler: function(){
					win.hide();
					alert('settings saved');
			}},{
				text:'Close', 
				handler: function(){
					win.hide();
				}
			}]
		});
	}
	win.show(this);
};

function showFriends(){
return "<br><form>\
		<input type='checkbox' name='friends' value='Dave Bergman'>Dave Bergman<br>\
		<input type='checkbox' name='friends' value='Paul Casperson'>Paul Casperson<br>\
		<input type='checkbox' name='friends' value='Alex Mohr'>Alex Mohr<br>\
		<input type='checkbox' name='friends' value='Mike Phelan'>Mike Phelan<br>\
		<input type='checkbox' name='friends' value='Brian Smith'>Brian Smith<br>\
		<input type='checkbox' name='friends' value='Justin Tulloss'>Justin Tulloss<br>\
		</form>";
};
