function PlaylistMgr() {
	var my = this;

	function beforeexpand(playlist) {
		if (expanded_playlist != playlist)
			last_expanded_playlist = expanded_playlist;
		expanded_playlist = playlist;
		return true;
	}
	function oncollapse(playlist) {
		if (expanded_playlist == playlist) {
			last_expanded_playlist.panel.expand();
		}
	}
	my.playqueue = new PlayQueue(
					{beforeexpand:beforeexpand,
					 oncollapse:oncollapse});

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
	var last_expanded_playlist = my.playqueue;
	function onremove(playlist) {
		delete open_playlists[playlist.id];
		
		my.panel.remove(playlist.panel);
		if (last_expanded_playlist == playlist) {
			last_expanded_playlist = my.playqueue;
		}

		if (!my.panel.layout.activeItem) {
			//Have to find a playlist to take this playlists place as the 
			//last_expanded_playlist when the current last_expanded_playlist
			//gets set as the active playlist
			var playlist_found = false;
			for (playlist_id in open_playlists) {
				if (open_playlists[playlist_id] != last_expanded_playlist) {
					expanded_playlist = open_playlists[playlist_id];
					playlist_found = true;
				}
			}
			if (!playlist_found)
				expanded_playlist = last_expanded_playlist;
			last_expanded_playlist.panel.expand();
		}
		else
			my.panel.doLayout(true);
	}

	var open_playlists = {};

	my.playqueue.on('collapse', oncollapse);
	my.playqueue.on('beforeexpand', beforeexpand);

	my.open_playlist = function(record) {
		if (open_playlists[record.get('Playlist_id')]) {
			//expanded_playlist = null;
			open_playlists[record.get('Playlist_id')].panel.expand();
			return;
		}

		playlist = new Playlist(
						{record: record, 
						 beforeexpand:beforeexpand,
						 oncollapse:oncollapse});
		playlist.on('remove', onremove);

		my.panel.add(playlist.panel);
		if (my.panel.rendered)
			my.panel.doLayout(true);
		//expanded_playlist = null;
		//I don't like the timeout method, but I couldn't get autoexpanding
		//working any other way. Seriously.
		setTimeout(function() {playlist.panel.expand();}, 100);

		open_playlists[record.get('Playlist_id')] = playlist;
	}

	my.enqueue = function(records) {
		expanded_playlist.enqueue(records);
	}

	var delete_dlg = new Ext.Template(
		'<h1>Delete Playlist</h1>',
		'<h2>{name}</h2>',
		'<br />',
		'<a href="#/action/playlist/delete/{id}" class="a-button">delete</a>',
		'<a href="#/action/dlg/hide" class="a-button">cancel</a>');
									
	my.delete_playlist = function(record) {
		show_dialog(delete_dlg.apply({
			name: record.get('Playlist_name'),
			id: record.get('Playlist_id')
		}));
	}

	urlm.register_action('playlist', function(rest) {
		var del_match = rest.match(/^delete\/(\d+)$/);
		if (del_match) {
			Ext.Ajax.request({
				url: '/playlist/delete/' + del_match[1],
				success: function() {
					show_status_msg('Playlist deleted!');
					bread_crumb.reload_playlist();
				},
				failure: function() {
					show_status_msg('Error deleting playlist');
				}
			});
			hide_dialog();
			return;
		}
	});
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
						playqueue.insert([config.record], true);
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

	my.insert = function(records) {
		if (!own_record(records[0])) {
			show_status_msg(
			'Cannot add other people\'s music to your playlists');
			return;
		}
		else
			songqueue.insert(records);
	}
	my.enqueue = function(records) {
		if (!own_record(records[0])) {
			show_status_msg(
			'Cannot add other people\'s music to your playlists');
			return;
		}
		else
			songqueue.enqueue(records);
	}
			
	my.panel.on('collapse', function() {
			return config.oncollapse(my);
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

function playlist_dblclick(record) {
	if (record.get('Friend_id') === undefined || 
		record.get('Friend_id') === global_config.uid) {
			playlistmgr.open_playlist(record);
	}
	else {
		playqueue.insert([record]);
	}
}
