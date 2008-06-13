/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *
 *  Updated 11/6/07 (r43) to support ExtJS --JMT
 *  Updated 03/08/08 (r162) to not suck --JMT
 *  Updated 04/08/08 (r548b875ae2a9) to support custom Node UIs --JMT
 *  Updated 05/17/08 to remove the now playing and tweak the UI --JMT
 */

function PlayQueue()
{
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

	var songQueue = new SongQueue();
	my.panel = songQueue.panel;

    my.enqueue = function(records) {
		songQueue.enqueue(records);
    }

    my.dequeue = function () {
		if (!songQueue.dequeue(playnow))
			my.fireEvent('stop');
    }

	function onreorder() {
		if (my.playing == null) {
			my.dequeue();
		}
		songQueue.peek(function(record) {
			my.fireEvent('buffersong', record);});
	}

	songQueue.on('reordered', onreorder);

    my.playgridrow = function(grid, songindex, e) {
        playnow(grid.store.getAt(songindex));
    }

    function playnow(record) {
        if (my.playing != null) {
            my.played.push(my.playing);
			my.playing.set('type', 'prevsong');
        }

        play(record);
    }

    function play(record) {
        if (record) {
			my.playing = record;
			record.set('type', 'nowplayingsong');
            my.fireEvent('playsong', record);
        }
    }

    my.prev = function() {
        if (showingprev) {
            my.hideprev();
            var show = true;
        }

        if (my.playing) {
			my.playing.set('type', 'song');
            songQueue.insert([my.playing]);
        }

        var record = my.played.pop();
        if (record)
            play(record);
        else {
            my.fireEvent('stop');
        }

        if (show) my.showprev();
    }

    my.showprev = function showprev() {
        showingprev = true;
        if (my.playing) {
            songQueue.insert([my.playing]);
            my.showingplaying = true;
        }
        for (i = my.played.length-1; i>=my.played.length-5; i--) {
            if (my.played[i]) {
                songQueue.insert([my.played[i]]);
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
}
Ext.extend(PlayQueue, Ext.util.Observable);

function SongQueue() {
	var my = this;

	my.addEvents({
        reordered : true,
	});
	
    var instructions = '<table id="queue-instructions"><tr><td>'+
        'Drag here to add songs'+
        '<br>-OR-<br>'+
        'Hit the <img class="middle" src="/images/enqueue.png" /> button'+
		'</td></tr></table>';

    my.root = new Ext.tree.TreeNode({expanded:true});
    my.tree = new Ext.tree.TreePanel({
        root: my.root,
        id: 'queuetree',
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
        border: false,
        hideBorders: true,
        header: false,
        html: instructions
    });

    my.panel = new Ext.Panel({
        id: 'queuepanel',
        region: 'west',
        split: true,
        width: '250px',
        titlebar:false,
        layout: 'card',
        cls: 'queue',
        activeItem: 0,
        items: [my.inspanel, my.tree]
    });

	my.enqueue = function(records) {
        for (i = 0; i < (records.length); i++) {
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
        return new typeinfo[type].nodeclass(config);
    }

	function update_instructions() {
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
        if (data.selections)
			my.enqueue(data.selections);
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
        }
    }
    
    my.insert = function insert(records, last) {
        if (records[0].type == "friend_radio") {
            if (my.is_friend_radio()) {
                return;    
            }
        }

		if (!last && my.root.hasChildNodes())
			last = my.root.item(0);

        for (var i = 0; i < (records.length); i++) {
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
    my.tree.on('checkchange', remove);
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

    this.dequeue = function(k) {};
	this.peek = function(k) {};
    this.update_text = function () {};
	this.is_active = function() { return !(this.config.inactive); }
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

    SongQueueNode.superclass.constructor.call(this, config);

    this.dequeue = function(k) {
        this.remove();
        k(this.record);
    }

	this.peek = function(k) {
		k(this.record);
	};
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
    config.draggable = true;
    config.checked = false;
    config.allowDrop = false;
    config.expandable = true;
    config.leaf = false;

    this.songs = new Ext.data.JsonStore({
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
    this.songs_loaded = false;

    AlbumQueueNode.superclass.constructor.call(this, config);

    this.dequeue = function(k) {
		function dequeue_aux() {
			var record = my.firstChild.record;
			my.firstChild.remove();
			my.update_text();
			k(record);
		}

		ensure_loaded(dequeue_aux);
    }

	my.peek = function(k) {
		ensure_loaded(function() { k(my.firstChild.record);});
	}

    this.update_text = update_text;
    function update_text()
    {
        this.setText(String.format('{0} ({1}/{2})',
            this.record.get('Album_title'),
            this.childNodes.length,
            this.record.get('Album_totaltracks')
        ));
        if (this.childNodes.length == 0) /* end of album */
            this.remove();
    }

    function on_expand(node) {
        ensure_loaded();
    }

	var loading = false;
	var actions = [];
	function ensure_loaded(k) {
		if (!my.songs_loaded) {
			if (k) actions.push(k);
			if (!loading) {
				loading = true;
				my.songs.load({
					callback: songs_callback,
				});
			}
		}
		else if(k) k();
	}

    function songs_callback(records, options, success) {
        if (!success) {
            alert("Something messed up");
            return;
        }

        my.songs_loaded = true;
        queue_songs();

		loading = false;
		for (var i=0; i<actions.length; i++) {
			actions[i]();
		}
		actions = [];
    }

    function queue_songs() {
        my.songs.each(function(record) {
            var nn = new SongQueueNode({
                queue: my.queue, 
                record: record,
				albumNode: true
            });
            my.appendChild(nn);
        });
    }

    this.on('expand', on_expand, this);
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
    albums.on('load', loaded, this);

    function loaded(store, records, options)
    {
        if (records.length > 0) {
			my.queue.insert(records, my);
        }
		my.remove();
    }
}
Ext.extend(ArtistQueueNode, QueueNode);

function FriendRadioQueueNode(config)
{
	var my = this;
	var current_song = null;

    config.text = String.format('Friend Radio');
    config.draggable = true;
    config.checked = false;
    config.allowDrop = true;
    config.expandable = false;
    config.leaf = true;

    FriendRadioQueueNode.superclass.constructor.call(this, config);

    this.dequeue = function(k) {
		//this is where we send the ajax request to find the new song.
		//when the song is returned, call k(song) on it.
        radio_handler = function(response, options) {
            var next_song = untyped_record(response);
            next_song.type = "song";
            k(next_song);
            current_song = next_song;
        }
        
        radio_handler_failure = function(response, options) {
            alert("next song couldn't be retrieved.  fuxx0red.");
        }
        
        request_next_song(radio_handler, radio_handler_failure);
    }
    
    function request_next_song(success_handler, failure_handler) {
        Ext.Ajax.request({
            url:'/metadata/next_radio_song',
            success: success_handler,
            failure: failure_handler
        });
    }
    
	my.peek = function(k) {
	    function success(response, options) {
	        var next_song = eval('(' + response.responseText + ')');
	        next_song = next_song.data[0];
	        next_song.get = (function(key) { return next_song[key];});
	        next_song.type = "song";
	        k(next_song);
	    }
	    
	    function failure(response, options) {
            alert("retrieving next song failed for buffering purposes");	    
	    }
	    
	    request_next_song(success, failure);
	}
}
Ext.extend(FriendRadioQueueNode, QueueNode);
