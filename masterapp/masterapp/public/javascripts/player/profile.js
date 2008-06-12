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
			container.child('.comment-controls').setDisplayed(true);
			container.child('.comments-body').setDisplayed(false);
		}
	}
    //this function is called whenever the profile page is loaded
	profile_handler = function(rest) {
		hide_all();
		
		var components = rest.split('/');
		
		if (components.length != 3 || (components[1] != 'spcomments' && components[1] != 'spedit')) {
			return;
		}
        var spot_id = components[2];		
		//if the user clicked the edit spotlight link, this code is executed: 
		if (components[1] == 'spedit') {
    		Ext.Ajax.request({
                url: '/metadata/spotlight_lookup',
                params: {id: spot_id},
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
        } else if (components[1] == 'spcomments') {		 //the user must've clicked the add comment link 
		    var target = Ext.get('spot-comment-'+spot_id);
		    if (target) {
    			target.child('.comment-controls').setDisplayed(false);
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
