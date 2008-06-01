// vim:noexpandtab
var check_url; //assigned in init_url_manager

urlm = {}; //urlmanager is a singleton

(function() {
    var my = urlm;

	var panel_lookup = {};
	var submanagers = [];
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

	function set_active(url) {
		if (panel_lookup[url] !== undefined) {
			viewmgr.centerpanel.layout.setActiveItem(panel_lookup[url]);
			return true;
		}
		else
			return false;
	}

	function add_panel(obj, url) {
		viewmgr.centerpanel.add(obj);
		panel_lookup[url] = obj.id;
	}

	/*Function goes to a url and gets it from the cache if possible.
	  will call function k if defined passing in the newly created panel */
	function goto_page_directly(url, k) {
		var autoLoad = {url: url};
		if (k)
			autoLoad.callback(k)

		var new_panel = new Ext.Panel({autoLoad: autoLoad});

		add_panel(new_panel);
		set_active(url);
	}

    function goto_page(url) {
		current_url = url;

		if (set_active(url))
			return;

		/* First check for a different handler function */
		for (var i=0; i<submanagers.length; i++) {
			var current = submanagers[i];
			var pattern = current[0](url);
			if (pattern) {
				var matched = pattern[0];
				var rest = url.substring(matched.length);
				current[1](matched, rest);
				return;
			}
		}

		//If there are no handlers
		goto_page_directly(url);
	}

	check_url = function() {
		var new_url = get_url(location.hash);
		if (current_url != new_url) {
			goto_page(new_url);
		}
	};

    /* Public functions */
	my.init = function(moremanagers) {
		my.register_handlers(moremanagers);
		setInterval('check_url();', 100);
	}

	//submanagers should be a list of (url component, handler function) pairs
    my.register_handlers = function(moremanagers) {

		//Convert all the patterns into regular expressions and make sure they
		//match the beginning of a string
		for (var i=0; i<moremanagers.length; i++) {
			var current = moremanagers[i];
			if (current[0][0] === '^')
				current[0] = RegExp(current[0]);
			else
				current[0] = RegExp('^'+current[0]);
		}

        submanagers = submanagers.concat(moremanagers);
    };

	my.ignore_matched = function(handler) {
		return function(matched, rest) {
			handler(rest);
		};
	};

	my.handle_matched = function(handler) {
		return function(matched, rest) {
			goto_page_directly(matched, 
					function(panel) {handler(rest);});
		};
	};

	my.generate_panel = function(handler) {
		return function(matched, rest) {
			new_panel = handler(rest);
			var complete_url = matched+rest;
			add_panel(new_panel, complete_url);
			set_active(complete_url);
		}
	}
	
	my.goto_url = function(url, params) {
        if(params) {
            url = [url, '?', Ext.urlEncode(params)].join('');
        }
		location.hash = '#'+url;
        return url;
	}
})();
