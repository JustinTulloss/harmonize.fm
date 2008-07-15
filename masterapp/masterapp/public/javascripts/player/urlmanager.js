// vim:noexpandtab
Hfm.urlm = {}; //urlmanager is a singleton
var urlm = Hfm.urlm; //for backwards compatibility

(function() {
    var my = Hfm.urlm;

	var panel_lookup = {};
	var submanagers = [];
	//Since we are always serving home page we need to detect when the user is
	//at a different page
	var last_url_matched = 'undefined';
	var current_url = 'undefined';
	var current_panel;
    
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
		viewmgr.centerpanel.layout.setActiveItem(obj.id);
		/*
		if (panel_lookup[url]) {
			Ext.get(panel_lookup[url]).remove();
		}
		panel_lookup[url] = obj.id;
		*/
		if (current_panel) {
			viewmgr.centerpanel.remove(current_panel.id);
			current_panel.remove();
		}
		

		current_panel = obj;
	}

	/*Function goes to a url and gets it from the cache if possible.
	  will call function k if defined passing in the newly created panel */
	function goto_page_directly(url, k) {
		var new_panel = document.createElement('div');
		new_panel.className = 'content-container';
		new_panel.show = function() {};

		add_panel(Ext.get(new_panel), url);
		
		Ext.Ajax.request({
			url: url,
			success: function(response) {
				new_panel.innerHTML = response.responseText;
				if (k)
					k(new_panel);
			}
		});

		//set_active(url);
	}

    function goto_page(url) {
		current_url = url;

		//if (set_active(url))
		//	return;

		/* First check for a different handler function */
		for (var i=0; i<submanagers.length; i++) {
			var current = submanagers[i];
			var pattern = url.match(current[0]);
			if (pattern) {
				var matched = pattern[0];
				var rest = url.substring(matched.length);
				current[1](matched, rest);
				last_url_matched = matched;
				return;
			}
		}

		//If there are no handlers
		goto_page_directly(url);
		last_url_matched = url;
	}

	check_url = function() {
		var new_url = get_url(location.hash);
		if (current_url != new_url) {
			goto_page(new_url);
		}
	};

	var url_actions = {};
	var url_actions_regex = RegExp('#/action/([^/]*)(/(.*))?$');
	function init_url_actions() {
		Ext.getBody().on('click', function(e, target) {
			var anchor;
			if (target.tagName=='A')
				anchor = target
			else {
				var target_el = new Ext.Element(target);
				anchor = target_el.findParent('a');
			}
			if (anchor) {
				var match = 
						anchor.getAttribute('href').match(url_actions_regex);
				if (match) {
					e.preventDefault();
					if (url_actions[match[1]]) {
						url_actions[match[1]](match[3], anchor);
					}
				}
			}
		});
	}

    /* Public functions */
	my.init = function(moremanagers) {
		my.register_handlers(moremanagers);
		setInterval('check_url();', 100);
		init_url_actions();
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
			function nhandler() {
				handler(rest);
			}
			if (matched == last_url_matched)
				nhandler();
			else {
				goto_page_directly(matched, nhandler);
			}
		};
	};

	my.generate_panel = function(handler) {
		return function(matched, rest) {
			new_panel = handler(rest);
			var complete_url = matched+rest;
			add_panel(new_panel, complete_url);
			//set_active(complete_url);
		}
	};
	
	my.goto_url = function(url, params) {
        if(params) {
            url = [url, '?', Ext.urlEncode(params)].join('');
        }
		location.hash = '#'+url;
        return url;
	}

	my.invalidate_page = function() {
		current_url = 'undefined';
		last_url_matched = 'undefined';
	}

	my.register_action = function(action, handler) {
		url_actions[action] = handler;
	}

	my.unregister_action = function(action) {
		delete url_actions[action];
	}
})();
