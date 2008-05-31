var check_url; //assigned in init_url_manager

function init_url_manager() {
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
		if (panel_lookup[url] !== undefined) {
			viewmgr.centerpanel.layout.setActiveItem(panel_lookup[url]);
		}
		else {
			function page_fetched(response) {
				var el = document.createElement('div');
				el.id = get_guid();
				el.innerHTML = response.responseText;

				viewmgr.centerpanel.add(Ext.get(el));
				viewmgr.centerpanel.layout.setActiveItem(el.id);
				panel_lookup[url] = el.id;

				initialize_links();
			}


			Ext.Ajax.request({
				url: url,
				success: page_fetched
			});
		}
		current_url = url;
	}
		

	function onLinkClick(e, target) {
		var url = get_url(target.hash);
		goto_page(url);
	}

	function is_internal_link(link) {
		if ( (link.href && link.href.indexOf('#') != -1) &&
			 ( (link.pathname == location.pathname) ||
			   ('/'+link.pathname == location.pathname)) &&
			 (link.search == location.search)) {
			return true;
		}
		else return false;
	}

	function initialize_links() {
		var tags = document.getElementsByTagName('a');
		for (var i=0; i<tags.length; i++) {
			var current = tags[i];
			if (is_internal_link(current)) {
				if (!current.urlmanaged) {
					current.urlmanaged = true;
					Ext.get(current).on('click', onLinkClick);
				}
			}
		}
	}

	initialize_links();

	check_url = function() {
		var new_url = get_url(location.hash);
		if (current_url != new_url) {
			goto_page(new_url);
		}
	}
	
	setInterval('check_url();', 200);
}
