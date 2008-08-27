/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *
 *  Updated 11/6/07 (r43) to support ExtJS --JMT
 *  Updated 03/08/08 (r162) to not suck --JMT
 *  Updated 04/08/08 (r548b875ae2a9) to support custom Node UIs --JMT
 *  Updated 05/17/08 to remove the now playing and tweak the UI --JMT
 */
var flattened = 0;
var async_act = 0;
function PlayQueue(config) {
    var showingprev = false;
    var my = this;

    my.addEvents({
        newsong : true,
        playsong: true,
        stop : true,
		buffersong: true
    });

    my.played = new Array(); /* Just an array of all the played treenodes */
    my.playing = null;

	var songQueue = new SongQueue('Play Queue');
	my.songQueue = songQueue;
	my.panel = songQueue.panel;

    my.enqueue = function(records) {
		songQueue.enqueue(records);
		if (my.playing === null)
			my.dequeue();
    }

    my.dequeue = function () {
		if (!songQueue.dequeue(playnow)) {
			my.fireEvent('stop');
			if (my.playing !== null) {
				my.played.push(my.playing);
				my.playing = null;
			}
		}
    }

	my.insert = function(records, playnow) {
		//var was_playing = my.playing != null;
		songQueue.insert(records);
		if (playnow || my.playing === null) {
			my.dequeue();
		}
	}

	function onreorder() {
		songQueue.peek(function(record) {
			my.fireEvent('buffersong', record);});
	}

	songQueue.on('reordered', onreorder);

    my.playgridrow = function(record) {
        if (Hfm.breadcrumb.is_friends_library()) {
            record.set('source', 1);
        } else {
            record.set('source', '0'); //this is a string b/c an int appears as undefined. wft?!
        }

        playnow(record);
    }

    function playnow(record) {
        if (my.playing != null) {
            my.played.push(my.playing);
        }

        play(record);
    }

    function play(record) {
        if (record) {
			my.playing = record;
            my.fireEvent('playsong', record);
        }
    }

    my.prev = function() {
        if (showingprev) {
            my.hideprev();
            var show = true;
        }

        if (my.playing) {
			//my.playing.set('type', 'song');
            songQueue.insert([my.playing]);
        }

        var record = my.played.pop();
        if (record)
            play(record);
        else {
			my.playing = null;
            my.fireEvent('stop');
        }

        if (show) my.showprev();
    }

    my.showprev = function showprev() {
        showingprev = true;
        if (my.playing) {
			my.playing.set('type', 'nowplayingsong');
            songQueue.insert([my.playing]);
			my.playing.set('type', 'song');
            my.showingplaying = true;
        }
        for (i = my.played.length-1; i>=my.played.length-5; i--) {
			var current = my.played[i];
            if (current) {
				current.set('type', 'prevsong');
                songQueue.insert([current]);
				current.set('type', 'song');
            }
            else
                break;
        }
    }

    my.hideprev = function() {
		if (showingprev) {
			showingprev = false;
			songQueue.clear_inactive();
		}
    }

	my.panel.on('beforeexpand', function() {
			return config.beforeexpand(my);
	});

	my.panel.on('collapse', function() {
			return config.oncollapse(my);
	});
	
	my.shuffle = function() {
	    songQueue.flatten(my.finish_shuffle); //after we flatten, we want to finish the shuffle
    }
    
    my.finish_shuffle = function() {
        //need to see if anything still hasn't been flattened
        if (flattened != 0) 
            return;    
        songQueue.shuffle();
    }

    my.is_friend_radio = songQueue.is_friend_radio;

    my.clear = clear;
    function clear() {
        songQueue.clear();
    }
}
Ext.extend(PlayQueue, Ext.util.Observable);

function SongQueue(label, is_playlist) {
	var my = this;

	my.addEvents({
        reordered : true
	});
	
    var instructions = '<table class="queue-instructions"><tr><td>'+
        'Drag here to add songs'+
        '<br>-OR-<br>'+
        'Hit the <img class="middle" src="/images/enqueue.png" /> button'+
		'</td></tr></table>';

    my.root = new Ext.tree.TreeNode({expanded:true});
    my.tree = new Ext.tree.TreePanel({
        root: my.root,
        cls: 'queuetree',
        rootVisible: false,
        layout: 'fit',
        height: '100%',
        autoScroll: true,
        containerScroll: true,
        enableDD: true,
        hlDrop: false,
        lines: false,
        dropConfig: {
            allowContainerDrop: true,
            onContainerDrop: paneldrop,
            onContainerOver: function(source, e, data){return this.dropAllowed;}
        }
    });

    my.inspanel = new Ext.Panel({
        title:"Instructions", 
        closable:false, 
        autocreate:true,
        layout: 'fit',
		height: '100%',
        border: false,
        hideBorders: true,
        header: false,
        html: instructions
    });
    
    my.panel = new Ext.Panel({
		title: label,
        titlebar:false,
		width: '100%',
        layout: 'card',
        cls: is_playlist ? 'playlist' : 'queue',
        activeItem: 0,
		hideCollapseTool: true,
		header: true,
        items: [my.inspanel, my.tree]
    });
    
    function get_source() {
        if (Hfm.breadcrumb.is_friends_library()) source = 1;
        else source = '0';
        if (location.vars != null) {
            source = location.vars.charAt(location.vars.indexOf('source') + 7);
        }
        return source;
    }

	my.enqueue = function(records) {
        source = get_source();
        for (i = 0; i < (records.length); i++) {
            records[i].set('source',source);
            var nn = newnode({record:records[i]});
            my.root.appendChild(nn);
        }
		reordered();
	}

	my.dequeue = function(k) {
		var node = first_active();
		if (node) {
			node.dequeue(function(record) {
				if (k) k(record);
				reordered();});
			return true;
		}
		else
			return false;
	}

    function newnode(config) {
        var type = config.record.get('type');
        config.queue = my;
		config.inactive = typeinfo[type].inactive;
		config.flatten = is_playlist;
        return new typeinfo[type].nodeclass(config);
    }

	function update_instructions() {
		if (typeof(my.panel.getLayout()) == 'string')
			return;

		if (my.root.firstChild)
			my.panel.getLayout().setActiveItem(1);
		else
			my.panel.getLayout().setActiveItem(0);
	}

    function remove(node, checked) {
        var p = node.parentNode;
        node.remove();
        if (p.update_text)
            p.update_text();

		reordered();
        /* this is in here because things are weird. Not having it caused
         * the page to reload. Yeah, weird. Something to do with replacing
         * the checkbox with a link. All sorts of bad.
         */
        Ext.EventObject.stopEvent();
    }

    function reordered() {
        my.fireEvent('reordered');
		update_instructions();
    }

    function paneldrop(source, e, data) {
		records = data.selections;
        if (records) {
			if (is_playlist && !own_record(records[0])) {
				show_status_msg('Cannot add friend\'s music to playlists!');
				return;
			}
			my.enqueue(data.selections);
		}
    }

    function treedrop(e) {
        var nodes = [];
        if (e.data.selections) {
            for (var i=0; i < e.data.selections.length; i++) {
                var row = e.data.selections[i];
                nodes.push(newnode({
                    record: row,
                    queue: my
                }));
            }
            e.dropNode = nodes;
            e.cancel = false;
			reordered();
        }
    }
    
    my.insert = function insert(records, last) {
		if (records.length == 0) {
            return;
        }
        if (records[0].type == "friend_radio") {
            if (my.is_friend_radio()) {
                return;    
            }
        }
        

		if (!last && my.root.hasChildNodes())
			last = my.root.item(0);
        
        source = get_source();
        if (location.hash.indexOf('source') != -1) // this means the source has been passed in the url
            source = location.hash.charAt(location.hash.indexOf('=') + 1);
        for (var i = 0; i < (records.length); i++) {
            records[i].set('source', source);
            var nn = newnode({record:records[i]});
            if (last) 
                my.root.insertBefore(nn, last);
            else {
                my.root.appendChild(nn);
			}
        }
		reordered();
    }

    my.is_friend_radio = function() {
        if (!my.root.hasChildNodes()) return false;        
        var node = my.root.firstChild;        
        if (node.config.record.type == "friend_radio") {
            return true;
        }
        else return false;        
    }

	my.clear_inactive = function() {
		while (my.root.firstChild && !my.root.firstChild.is_active())
			my.root.firstChild.remove();
	}

    my.clear = function() {
        while (my.root.firstChild) {
            my.root.firstChild.remove();
        }
    }

	my.peek = function(k) {
		var node = first_active();
		if (node)
			node.peek(k);
	}

	function first_active() {
		for (var i=0; my.root.item(i) && !(my.root.item(i).is_active()); i++);
		return my.root.item(i);
	}
    
    my.inspanel.on('render', function() {
        var dtarget = new Ext.dd.DropTarget(my.panel.getEl(), {
            notifyDrop: paneldrop,
            ddGroup: 'TreeDD'
        });
		my.inspanel.on('show', function() {
			dtarget.isTarget = true;
		});
		my.inspanel.on('hide', function() {
			dtarget.isTarget = false;
		});
    });
    my.tree.on('bodyresize', function(){
        if (my.tree.dropZone)
            my.tree.dropZone.setPadding(0,0,my.tree.getInnerHeight(),0);
    });
    my.tree.on('beforenodedrop', treedrop);
    my.tree.on('movenode', reordered);
	//my.tree.on('remove', reordered);
    my.tree.on('checkchange', remove);
    
    my.flatten = flatten;
    function flatten(func) {
        var len = my.root.childNodes.length;
        for (i = (len - 1); i >=0; --i) {
            if (!my.root.item(i).isLeaf())
                ++flattened;
            my.root.item(i).flatten(func); //this calls playqueue.finish_shuffle() when all flattens return
        }
    }
    
    my.shuffle = function() {
        var num_songs = my.root.childNodes.length;
        while (num_songs > 1) {
            var rand = Math.floor(Math.random()*num_songs);
            --num_songs;
            swap(rand, num_songs);
        }
    }
    
    function swap(a,b) {
        if (a == b) return;
        
        var atemp = my.root.item(a);
        var btemp = my.root.item(b);
        
        my.root.insertBefore(btemp,my.root.item(a-2));
        my.root.insertBefore(atemp,my.root.item(b-1));
    }
}
Ext.extend(SongQueue, Ext.util.Observable);

/* A node for a queue. This mostly just builds the treenode, but it also
 * needs to know how to manipulate that node when things happen. Like when it's
 * being prefetched or when it's time for this node to be played. It's all quite
 * complex.
 */
function QueueNode(config)
{
    this.config = config;
    if (this.config.uiProvider == null)
        this.config.uiProvider = QueueNodeUI;

    QueueNode.superclass.constructor.call(this, config);

    /* Prototype for QueueNodes, meant to be extended */
    this.record = config.record;
    this.queue = config.queue;
	this.loaded = false;
    
    this.dequeue = function(k) {};
	this.peek = function(k) {};
    this.update_text = function () {};
	this.is_active = function() { return !(this.config.inactive); }
	
	this.flatten = function(func) {
        func();
	};
}
Ext.extend(QueueNode, Ext.tree.TreeNode);

function SongQueueNode(config)
{
	if (config.record.get('Artist_name') && !config.albumNode) {
		config.text = config.record.get('Song_title')+' - '+
						config.record.get('Artist_name');
	}
	else
		config.text = config.record.get('Song_title');
    config.checked = false;
    config.leaf = true;
	config.draggable = true;
	if (config.inactive)
		config.disabled = true;

	this.songid = config.record.get('Song_id');
    
    SongQueueNode.superclass.constructor.call(this, config);
    
    this.dequeue = function(k) {
        this.remove();
        k(this.record);
    }

	this.peek = function(k) {
		k(this.record);
	};

	this.loaded = true;
    
}
Ext.extend(SongQueueNode, QueueNode);

function PlayingQueueNode(config) {
    config.title = config.record.get('Song_title');
    config.artist = config.record.get('Artist_name');
    config.album = config.record.get('Album_title');
    config.leaf = true;
    config.checked = null;
    config.draggable = false;
    config.allowDrop = false;
    config.allowDrag = false;
    config.uiProvider = PlayingNodeUI;
    config.index = 0;

    SongQueueNode.superclass.constructor.call(this, config);
    this.dequeue = function(k) {this.remove();};
}
Ext.extend(PlayingQueueNode, QueueNode);

function AlbumQueueNode(config)
{
	var my = this;

    config.text = String.format('{0} ({1}/{2})', 
        config.record.get('Album_title'),
        config.record.get('Album_havesongs'),
        config.record.get('Album_totaltracks')
    );
    config.artist = config.record.get('Artist_name');
    config.draggable = true;
    config.checked = false;
    config.allowDrop = false;
    config.expandable = true;
    config.leaf = false;

	my.loading = true;

    var songs = new Ext.data.JsonStore({
        url: 'metadata',
        root: 'data',
        sortInfo: {field: 'Song_tracknumber', direction: 'ASC'},
        baseParams: {
            type:'song', 
            album: config.record.get('Album_id'),
            friend: config.record.get('Friend_id')
        },
        successParameter: 'success',
        autoLoad: false,
        fields: global_config.fields.song
    });

    AlbumQueueNode.superclass.constructor.call(this, config);

    this.dequeue = function(k) {
		function dequeue_aux() {
			var record = my.firstChild.record;
            record.set('source',config.record.get('source'));
			my.firstChild.remove();
			update_text();
			k(record);
		}

		ensure_loaded(dequeue_aux);
    }

	my.peek = function(k) {
		ensure_loaded(function() { 
			if (!my.firstChild)
				return;
			k(my.firstChild.record);
		});
	}

    function update_text() {
        my.setText(String.format('{0} ({1}/{2})',
            config.record.get('Album_title'),
            my.childNodes.length,
            config.record.get('Album_totaltracks')
        ));
        if (my.childNodes.length == 0) /* end of album */
            my.remove();
    }

	var loading = false;
	var actions = [];
	function ensure_loaded(k) {
		if (!my.loaded) {
			if (k) actions.push(k);
			if (!loading) {
				loading = true;
				songs.load({
					callback: songs_callback
				});
			}
		}
		else if(k) k();
	}

    function songs_callback(records, options, success) {
        if (!success) {
            show_status_msg('Error loading album!');
            return;
        }

        my.loaded = true;
        queue_songs();

		loading = false;
		for (var i=0; i<actions.length; i++) {
			actions[i]();
		}
		actions = [];
    }

    function queue_songs() {
		if (config.flatten) {
			my.queue.insert(songs.getRange(), my);
			my.remove();
		}
		else {
			songs.each(function(record) {
				var nn = new SongQueueNode({
					queue: my.queue, 
					record: record,
					albumNode: true
				});
				my.appendChild(nn);
			});
		}
    }

	if (config.flatten)
		ensure_loaded();

    this.on('expand', function() {ensure_loaded();});
    
    my.flatten = flatten;
    function flatten(func) {
        ensure_loaded(function() {
            var nodes = my.childNodes;
            var records = [];
            for (i = 0; i < nodes.length; i++) {
                records.push(nodes[i].record);
            }
            my.queue.insert(records, my);
			my.remove();
			--flattened;
			func(); // this is the end-all callback function for all node types
        });
    }
}
Ext.extend(AlbumQueueNode, QueueNode);

function ArtistQueueNode(config)
{
    var my = this;
    config.text = 'Loading...';
    ArtistQueueNode.superclass.constructor.call(this, config);

    var albums = new Ext.data.JsonStore({
        url: 'metadata',
        root: 'data',
        sortInfo: {field: 'Album_title', direction: 'ASC'},
        baseParams: {
            type:'album', 
            artist: config.record.get('Artist_id'), 
            friend: config.record.get('Friend_id')
        },
        successParameter: 'success',
        autoLoad: true,
        fields: global_config.fields.album
    });
    albums.on('load', loaded);

    function loaded(store, records, options) {
        if (records.length > 0) {
			my.queue.insert(records, my);
        }
		my.remove();
		if (last_k)
			config.queue.dequeue(last_k);
    }

	var last_k = null;
	my.dequeue = function(k) {
		last_k = k;
	}
}
Ext.extend(ArtistQueueNode, QueueNode);

function PlaylistQueueNode(config) {
	var my = this;
	config.text = String.format('Playlist - {0} ({1}/{2})',
		config.record.get('Playlist_name'),
		config.record.get('Playlist_songcount'),
		config.record.get('Playlist_songcount')
	);
	config.draggable = true;
	config.allowDrop = false;
	config.expandable = true;
	config.leaf = false;
	config.checked = false;

	PlaylistQueueNode.superclass.constructor.call(this, config);

	function loaded(store, records) {
		if (records.length > 0) {
			my.queue.insert(records, my);
		}
		my.remove();
	}

	var songs = new Ext.data.JsonStore({
		url: '/metadata',
		root: 'data',
		baseParams: {
			type: 'song',
			playlist: config.record.get('Playlist_id'),
			friend: config.record.get('Friend_id')
		},
		successParameter: 'success',
		fields: global_config.fields.song
	});

    this.dequeue = function(k) {
		function dequeue_aux() {
			if (!my.firstChild) {
				my.remove();
				return;
			}
			var record = my.firstChild.record;
			my.firstChild.remove();
            record.set('source',config.record.get('source'));
			update_text();
			k(record);
		}

		ensure_loaded(dequeue_aux);
    }

	my.peek = function(k) {
		ensure_loaded(function() { 
			if (!my.firstChild)
				return;
			k(my.firstChild.record);
		});
	}

    function update_text() {
        my.setText(String.format('Playlist - {0} ({1}/{2})',
            config.record.get('Playlist_name'),
            my.childNodes.length,
            config.record.get('Playlist_songcount')
        ));
        if (my.childNodes.length == 0) /* end of album */
            my.remove();
    }

	var loading = false;
	var actions = [];
	function ensure_loaded(k) {
		if (!my.loaded) {
			if (k) actions.push(k);
			if (!loading) {
				loading = true;
				songs.load({
					callback: songs_callback
				});
			}
		}
		else if(k) k();
	}

    function songs_callback(records, options, success) {
        if (!success) {
            show_status_msg('Error loading playlist!');
            return;
        }

        my.loaded = true;
        queue_songs();
		loading = false;
		if (my.firstChild) { //Don't run anything if there aren't children
			for (var i=0; i<actions.length; i++) {
				actions[i]();
			}
			actions = [];
		}
    }

    function queue_songs() {
		if (config.flatten) {
            my.queue.insert(songs.getRange(), my);
            my.remove();
		}
		else {
			songs.each(function(record) {
				var nn = new SongQueueNode({
					queue: my.queue, 
					record: record,
					albumNode: true
				});
				my.appendChild(nn);
			});
		}
    }

	if (config.flatten)
		ensure_loaded();

    this.on('expand', function() {ensure_loaded();});
    
    my.flatten = flatten;
    function flatten(func) {
        ensure_loaded(function(){
            my.queue.insert(songs.getRange(), my);
			my.remove();     
			--flattened;  
			func();
        });
    }
}
Ext.extend(PlaylistQueueNode, QueueNode);

function FriendRadioQueueNode(config)
{
	var my = this;
	var next_song_g = null;
	var fetching = false;
    var peek_k = [];
    var dequeue_k = null;

    config.text = 'Friend Radio';
    config.draggable = true;
    config.checked = false;
    config.allowDrop = true;
    config.expandable = false;
    config.leaf = true;

    FriendRadioQueueNode.superclass.constructor.call(this, config);

	function get_next_song() {
	    function failure(response, options) {
			fetching = false;
            show_status_msg('Error getting song from server');
	    }

		function success(response) {
			var next_song = untyped_record(response);
			next_song.set('type', "song");
			next_song_g = next_song

			fetching = false;

			if (dequeue_k) {
				next_song_g = null;
				dequeue_k(next_song);
				dequeue_k = null;
				if (peek_k && !fetching) {
					get_next_song();
				}
			}
			else if (peek_k) {
				for (var i=0; i<peek_k.length; i++) {
					peek_k[i](next_song);
				}
				peek_k = [];
			}
		}

		fetching = true;
        Ext.Ajax.request({
            url:'/metadata/next_radio_song',
            success: success,
            failure: failure
        });
    }

    this.dequeue = function(k) {
        if (next_song_g) {
			var song = next_song_g;
			next_song_g = null;
			k(song);
		}
        else if (fetching) {
			peek_k = [];
            dequeue_k = k
        }
		else {
			dequeue_k = k;
			get_next_song();
		}
    }
    
	my.peek = function(k) {
		if (next_song_g) {
			k(next_song_g);
		}
	    else if (fetching)
	        peek_k.push(k);
	    else {
            peek_k.push(k);            
            get_next_song();
		}
	}
}
Ext.extend(FriendRadioQueueNode, QueueNode);
