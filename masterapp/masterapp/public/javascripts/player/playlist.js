function PlaylistMgr() {
	var my = this;

	function beforecollapse(playlist) {
		if (playlist === expanded_playlist)
			return false;
		else return true;
	}
	function beforeexpand(playlist) {
		expanded_playlist = playlist;
		return true;
	}
	my.playqueue = new PlayQueue(
					{beforeexpand:beforeexpand,
					 beforecollapse:beforecollapse});

	my.panel = new Ext.Panel({
		id: 'queuepanel',
		layout: 'accordion',
		region: 'west',
		width: '250px',
		split: true,
		titleCollapse: true,
		titlebar: false,
		header: false,
		items: [my.playqueue.panel]
	});

	var expanded_playlist = my.playqueue;
	function onremove(playlist) {
		delete open_playlists[playlist.id];
		
		my.panel.remove(playlist.panel);

		if (!my.panel.layout.activeItem)
			my.playqueue.panel.expand();
		else
			my.panel.doLayout(true);
	}

	var open_playlists = {};

	my.playqueue.on('beforecollapse', beforecollapse);
	my.playqueue.on('beforeexpand', beforeexpand);

	my.open_playlist = function(record) {
		if (open_playlists[record.get('Playlist_id')]) {
			expanded_playlist = null;
			open_playlists[record.get('Playlist_id')].panel.expand();
			return;
		}

		playlist = new Playlist(
						{record: record, 
						 beforeexpand:beforeexpand,
						 beforecollapse:beforecollapse});
		playlist.on('remove', onremove);

		my.panel.add(playlist.panel);
		if (my.panel.rendered)
			my.panel.doLayout(true);
		expanded_playlist = null;
		//I don't like the timeout method, but I couldn't get autoexpanding
		//working any other way. Seriously.
		setTimeout(function() {playlist.panel.expand();}, 100);

		open_playlists[record.get('Playlist_id')] = playlist;
	}

	my.enqueue = function(records) {
		expanded_playlist.enqueue(records);
	}
}

function Playlist(config) {
	var my = this;

	my.id = config.record.get('Playlist_id');

	my.addEvents({
		remove: true
	});

	var actions = {
		close_panel: function(panel) { 
						clearInterval(interval);
						my.fireEvent('remove', my);
					 },
		play_playlist: function(panel) {
						playqueue.insert([config.record]);
						playqueue.dequeue();
					}
	};

	var title = '<div class="playlist-button close_panel"></div><div class="playlist-button play_playlist"></div>' +
				config.record.get('Playlist_name');
	var songqueue = new SongQueue(title, true);
	my.panel = songqueue.panel;

	my.panel.on('titlechange', function(panel) {
		panel.getEl().select('.playlist-button').each(function(el) {
			for (var action in actions) {
				if (el.hasClass(action)) {
					(function(action) {
						el.on('click', function(e) {
							actions[action](panel);
							e.stopEvent();
						});
					})(action);
				}
			}
		});
	});

	my.insert = songqueue.insert;
	my.enqueue = songqueue.enqueue;
			
	my.panel.on('beforecollapse', function() {
			return config.beforecollapse(my);
	});
	my.panel.on('beforeexpand', function() {
			return config.beforeexpand(my);
	});

	var saving_playlist = false;

	//Returns true if it succeded in saving the playlist (no nodes were loading)
	function save_playlist() {
		saving_playlist = true;

		var i=0;
		var current = songqueue.root.firstChild;
		var songs = ''
		while (current) {
			if (!current.loaded)
				return false;

			var id = String(current.songid);
			if (songs == '')
				songs = id;
			else
				songs += ','+id;

			current = current.nextSibling;
			i++;
		}

		Ext.Ajax.request({
			url:'/playlist/save',
			params: {
				playlist:String(my.id),
				songs:songs
			},
			failure: function() {
						show_status_msg('Failed to save playlist!');
						saving_playlist = false;},
			success: function() {
						saving_playlist = false;}
		});

		config.record.set('Playlist_songcount', i);

		return true;
	}


	songqueue.insert([config.record]);

	//We don't want to save after inserting initial playlist
	var run_once = false;
	var dirty = false; 
	songqueue.on('reordered', function() { dirty = true; });
	function check_dirty() {
		if (dirty && !run_once) {
			run_once = true;
			dirty = false;
			return;
		}
		if (dirty && !saving_playlist) {
			var res = save_playlist();
			if (res)
				dirty = false;
		}
	}
	var interval = setInterval(check_dirty, 2000);
}
Ext.extend(Playlist, Ext.util.Observable);
