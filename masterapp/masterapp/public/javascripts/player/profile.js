/* Justin Tulloss
 * 05/31/08
 *
 * Takes care of javascript present on a profile page.
 */
var profile_handler;

(function() {
	function hide_all() {
		var pbody = Ext.get('profile-body');	
		var containers = pbody.query('.profile-sp-commentcontainer')
		for (var i=0; i<containers.length; i++) {
			var container = Ext.get(containers[i]);
			container.child('.view-comment').setDisplayed(true);
			container.child('.hide-comment').setDisplayed(false);
			container.child('.comments-body').setDisplayed(false);
		}
	}
    //this function is called whenever the profile page is loaded
	profile_handler = function(rest) {
		hide_all();
		
		var components = rest.split('/');
		//find all the edit_spotlight links and assign onclick handlers to them
		var edit_links = Ext.query('.edit-spotlight');

		for (i = 0; i < edit_links.length; i++) {
		    var spot_id = parseInt(edit_links[i].id);
            //this handler looks hackish because it solves a closure property (shudder)
            Ext.get(edit_links[i].id).removeAllListeners();
		    Ext.get(edit_links[i].id).on('click', (function(spot_id) {return function() {
    		    Ext.Ajax.request({
                    url: '/metadata/find_spotlight_by_id',
                    params: {id: parseInt(spot_id)},
                    success: function(response, options) {
                        record = eval('(' + response.responseText + ')');
                        record = record.data[0];
                        record['id'] = spot_id;
                        record.get = (function(key) { return record[key];});
                        show_spotlight(record, "edit");
                    },
                    failure: function(response, options) {
                        alert("failed to lookup spotlight");                
                    }
                });
		    };})(spot_id));
		}
		
		edit_links = Ext.query('.edit-playlist-spotlight');
		for (i = 0; i < edit_links.length; i++) {
		    var spot_id = parseInt(edit_links[i].id);
            //this handler looks hackish because it solves a closure property (shudder)
            Ext.get(edit_links[i].id).removeAllListeners();
		    Ext.get(edit_links[i].id).on('click', (function(spot_id) {return function() {
    		    Ext.Ajax.request({
                    url: '/metadata/find_playlist_spotlight_by_id',
                    params: {id: parseInt(spot_id)},
                    success: function(response, options) {
                        record = eval('(' + response.responseText + ')');
                        record = record.data[0];
                        record['id'] = spot_id;
                        record.get = (function(key) { return record[key];});
                        show_spotlight(record, "edit_playlist");
                    },
                    failure: function(response, options) {
                        alert("failed to lookup spotlight");                
                    }
                });
		    };})(spot_id));
		}
		
		
		if (components.length != 3 || components[1] != 'spcomments') {
			return;
		}
        var spot_id = components[2];		
		//if the user clicked the edit spotlight link, this code is executed: 
        		
		if (components[1] == 'spcomments') {		 //the user must've clicked the add comment link 
		    var target = Ext.get('spot-comment-'+spot_id);
		    if (target) {
    			target.child('.view-comment').setDisplayed(false);
				target.child('.hide-comment').setDisplayed(true);
			    target.child('.comments-body').setDisplayed(true);
			    
			    var button = target.child('.send-spot-comment');
			    if (!button.managed) {
    				button.managed = true;
				    button.on('click', function(e) {
    					e.preventDefault();
					    var textarea = target.child('.spot-comment-textarea');
					    Ext.Ajax.request({
    						url: '/people/add_spotcomment/'+spot_id,
						    params: {comment: textarea.dom.value},
						    success: function() {
    							show_status_msg('Comment added!');
							    urlm.invalidate_page();
						    }
					    });
				    });
			    }
		    }
	    }
    }

    var friend_music_menu_link = null;
    var friend_music_menu = null;

    function browse_friends_music(friend, target) {
        if (friend == null) return;
        
        friend_music_menu = new Ext.menu.Menu({
            width: target.offsetWidth,
            defaultAlign: 'tr-br',
            shadow: false
        });
        
        var urlbase = ['#/bc/friend=', friend, '/profile=', friend];
        friend_music_menu.add(new Ext.menu.Item({
            text: 'artists',
            href: urlbase.concat(['/artist']).join(''),
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'
        }));
        friend_music_menu.add(new Ext.menu.Item({
            text: 'albums',
            href: urlbase.concat(['/album']).join(''),
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'
        }));
        friend_music_menu.add(new Ext.menu.Item({
            text: 'songs',
            href: urlbase.concat(['/song']).join(''),
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'    
        }));
        friend_music_menu.add(new Ext.menu.Item({
            text: 'playlists',
            href: urlbase.concat(['/playlist']).join(''),
            itemCls: 'music-menu-item',
            overCls: 'music-menu-item-over',
            activeClass: 'music-menu-item-active',
            iconCls: 'no_icon'    
        }));
        friend_music_menu.show(target);
    }

    urlm.register_action('browse_friend', browse_friends_music);
})();

function profile_factory(url) {
    var newprofile = new Profile(url);
    return newprofile.panel;
}

function Profile(id)
{
    var my = this;
    my.panel = new Ext.Panel({
        layout: 'column',
        autoScroll: true,
        nocrumb: true,
        items: [{
            autoLoad: 'people/profile_body/'+id,
            layout: 'fit',
            columnWidth: .98
        },{
            autoLoad: 'people/profile_right/'+id,
            layout:'fit',
            width: 220
        }]
    });

    my.panel.on('show', function(){my.panel.syncSize()});

    urlm.register_handlers([
        ['/profile_comments/', view_comments],
    ]);

    my.go = function(url) {
        alert(url);
    }
    function view_comments(spotlightid)
    {
        alert(spotlightid);
    }
}
