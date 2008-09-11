/* Justin Tulloss
 * 03/04/2008
 *
 * In an effort to avoid this becoming a catchall for whatever functionality
 * we can't think to put anywhere else, there are a few rules on what goes here.
 *
 * This class is intended to manage what components are being displayed. It has
 * no knowledge of the underlying data whatsoever, just what components are
 * what. This means that it's hooked to a whole bunch of signals, and changes
 * what's displayed based on those signals. Don't put data dependent components
 * in here.
 */

/* just pass in the home panel's crumb for navigation and an object of objects
 * that viewmanager is supposed to manage
 */
function ViewManager(objects)
{
	var my = this;

	/*
    var homepanel = new Ext.Panel({
        title: "Home", 
        fitToFrame: true, 
        autocreate: true, 
        contentEl: 'home', 
        header: false,
		cls: 'homepanel',
        nocrumb: true
    });
	*/

    t_status = new Ext.Template(
        '<div id="status">',
			'<span class="playlist-controls">',
			'<a id="create-playlist" href="#">create playlist</a></span>',
			'<span class="playlist-controls"><a id="shuffle-playqueue" href="#">shuffle</a></span>',
            '<span class="playlist-controls"><a id="clear-playqueue" href="#">clear</a></span>',
            '<span class="uname">Welcome, {name:trim}</span>',
            '<span class="cstatus">{status}</span>',
        '</div>').compile();
    

	/*
    if (crumb)
        crumb.panel = homepanel;
	*/

    my.search_field = new Ext.form.TextField({
        emptyText: "Search...",
        enableKeyEvents: true,
        cls: 'searchfield'
    });


    var bcheight = 50;
    var bcpanel = new Ext.Panel({
        title: "Breadcrumb",
        height: bcheight,
        autocreate: true,
        anchor: '100%',
        header: false,
        layout: 'fit',
        items: [Ext.get('bccontent'), my.search_field]
    });

    var gridstack = new Ext.Panel({
        title: "Grids",
        layout: 'card',
        autocreate: true,
        anchor: '0 -' + bcheight,
        header: false
    });

    var statusbar = new Ext.Toolbar({
        height: 25,
		region: 'south',
        cls: 'status'
    });

    var browserpanel = new Ext.Panel({
        title: "Browser",
        autocreate: true,
        layout: 'anchor',
        header: false,
        items: [bcpanel, gridstack]
    });

	my.centerpanel = new Ext.Panel({
		region: 'center',
        id: 'centerpanel',
        layout: 'card',
        activeItem: 0,
        items: [browserpanel]
    });

    bigshow = new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            height: 65,
            border: false,
            bodyBorder: false,
            fitToFrame: true,
            layout: 'fit',
            height: 'auto',
            titlebar: false,
            contentEl: 'header',
			id: 'top-panel'
        }, 
        objects.queue.panel, 
		my.centerpanel,
		statusbar]
    });
    var username = global_config.fullname;

    urlm.register_action('reload', function(){
        var panel = my.centerpanel.getLayout().activeItem;
        if (panel == browserpanel) {
            Hfm.breadcrumb.reload();
		}
        else {
            urlm.invalidate_page();
		}
    });
    set_status(null);

    var music_menu_link = Ext.get('music_menu_link');
    var music_menu = new Ext.menu.Menu({
        id: 'music_menu',
        defaultAlign: 'tr-br',
        shadow: 'drop'
    });        

    function set_music_menu() {
        function show_menu(e) {
            e.preventDefault();
            music_menu.show(music_menu_link);
            //change the music link to a white background by setting the css class
            music_menu_link.addClass('active-menu');
        }
        
        function hide_menu(e) {
            e.preventDefault();
            music_menu.hide();
            music_menu_link.removeAllListeners();
            music_menu_link.on('click',show_menu);
        }
        
        function reset_menu_link(e) {
            //reset the menu's css class information
            music_menu_link.removeClass('active-menu');
        }
        music_menu.add(new Ext.menu.Item({
            text: 'artists',
            href: '#/browse/artist',
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'
        }));
        music_menu.add(new Ext.menu.Item({
            text: 'albums',
            href: '#/browse/album',
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'
        }));
        music_menu.add(new Ext.menu.Item({
            text: 'songs',
            href: '#/browse/song',
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'
        }));
        music_menu.add(new Ext.menu.Item({
            text: 'playlists',
            href: '#/browse/playlist',
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'
        }));
        music_menu_link.on('click', show_menu);
        music_menu.on('hide',reset_menu_link);
    }

	set_music_menu();

    this.set_panel= function(crumb, params, e) {
        if (crumb.panel) {
            if (crumb.panel.nocrumb) {
                center = bigshow.getComponent('centerpanel');
                if (!center.findById(crumb.panel.id)) {
                    center.add(crumb.panel);
				}
                center.getLayout().setActiveItem(crumb.panel.id);
                return;
            }
            else {
                if (!gridstack.findById(crumb.panel.id)){
                    gridstack.add(crumb.panel);
                }
                gridstack.getLayout().setActiveItem(crumb.panel.id);
                bigshow.getComponent('centerpanel').
                    getLayout().setActiveItem(browserpanel.id);
            }
        }
    };

    this.init_search = function(crumb, params, e) {
        if (crumb.panel) {
            /*my.search_field.validator = 
                function(text) {
					return crumb.panel.search.call(crumb.panel, text)};
            */
            my.search_field.allowBlank = true;
            my.search_field.on('keyup', function () {
                var text = this.getValue();
                return crumb.panel.search.call(crumb.panel, text);
            });
            
            my.search_field.on('blur', function(form){
                crumb.panel.search.call(crumb.panel, form.getValue());
            });
        }
    };

    this.add_card = function(newpanel, crumb) {
        bigshow.getComponent('centerpanel').add(newpanel);
        if (crumb) {
            crumb.panel = newpanel;
		}
    };

    this.set_status = function(text) {
        if (!text) {
            text = '<a href="#/action/reload">refresh</a>';
		}
        
        var el = statusbar.getEl().child('.cstatus');
		if (el) {
			el.update(text);
		}
		else {
			t_status.overwrite(statusbar.getEl(),{name: username,status: text});
		}
    };

	var create_playlist_dialog = 
		'<h1>Create a new Playlist</h1>' +
		'<center><table><tr>'+
		'<td id="create-playlist-form" class="dlg-form h-light-form">'+
		'<input id="playlist-name" maxlength="100" class="dlg-focus" />'+
		'<br/>playlist name<br/><br/>' +
		'<a class="a-button" href="#/action/dlg/hide">cancel</a>' +
		'<a class="a-button" href="#/action/playlist/create">create</a>' +
		'</td></tr></table></center>';
	Ext.get('create-playlist').on('click', function(e, el) {
		e.preventDefault();
		show_dialog(create_playlist_dialog);
	});
    
    Ext.get('shuffle-playqueue').on('click', playlistmgr.shuffle);    
    Ext.get('clear-playqueue').on('click', playlistmgr.clear);
}
