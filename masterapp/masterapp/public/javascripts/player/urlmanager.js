/* vim:noexpandtab */
var check_url; //assigned in init_url_manager

//submanagers should be a list of url component => handler function pairs
function UrlManager(submanagers) {
    var my = this;
	var panel_lookup = {};
	var guid = 0;
	//Since we are always serving home page we need to detect when the user is
	//at a different page
	var current_url = get_url(''); 

	panel_lookup['/player/home'] = 0;

	function get_url(hash) {
		if (hash === '' || hash === '#')
			return '/player/home';
		else
			return hash.substring(1);
	}

	function get_guid() {
		var res = 'urlm' + String(guid);
		guid++;
		return res;
	}

	function goto_page(url) {
        var new_panel = null;

        /* Check the cache */
		if (panel_lookup[url] !== undefined) {
			viewmgr.centerpanel.layout.setActiveItem(panel_lookup[url]);
            return;
		}

		/* Not cached, first check for a different handler function */
		for (var i=0; i<submanagers.length; i++) {
			var current = submanagers[i];
			var pattern = current[0];
			if (url.substring(0, pattern.length) === pattern) {
				current_url = url;
				new_panel = current[1](url.substring(pattern.length));
                if (new_panel == null)
                    return;
			}
		}

		if(new_panel == null) {
            new_panel = Ext.Panel({
                autoLoad: {
                    url: url
                }
            });
		}
        viewmgr.centerpanel.add(new_panel);
        viewmgr.centerpanel.layout.setActiveItem(new_panel.id);
        panel_lookup[url] = new_panel.id;

		current_url = url;
	}
		

	function onLinkClick(e, target) {
		var url = get_url(target.hash);
		goto_page(url);
	}

	check_url = function() {
		var new_url = get_url(location.hash);
		if (current_url != new_url) {
			goto_page(new_url);
		}
	}

	setInterval('check_url();', 200);

    /* Public functions */
    my.register_handlers = function(moremanagers)
    {
        submanagers = submanagers.concat(moremanagers);
    }

    my.goto_url = function(url, params)
    {
        if (params)
            url = [url, '?', Ext.urlEncode(params)].join('');
        location.hash = '#'+url;
        return url;
    }
}
