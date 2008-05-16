/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *
 *  Updated 11/6/07 (r43) to support ExtJS --JMT
 *  Updated 03/08/08 (r162) to not suck --JMT
 *  Updated 04/08/08 (r548b875ae2a9) to support custom Node UIs --JMT
 */

function PlayQueue()
{
    var fields = fields;
    var showingprev = false;

    this.addEvents({
        newsong : true,
        reordered : true,
        playsong: true,
        stop : true
    });

    var instructions = new Ext.Template(
        'Drag here to add songs',
        '<br>-OR-<br>',
        'Hit the <img class="middle" src="/images/enqueue.png" /> button'
    );
    instructions = instructions.compile();

    this.played = new Array(); /* Just an array of all the played treenodes */
    this.playing = null;
    this.root = new Ext.tree.TreeNode({expanded:true});
    this.tree = new Ext.tree.TreePanel({
        root: this.root,
        rootVisible: false,
        layout: 'fit',
        autoScroll: true,
        containerScroll: true,
        enableDD: true,
        ddGroup: 'GridDD',
        dropConfig: {
            allowContainerDrop: true,
            ddGroup: 'GridDD'
        }
    });

    this.inspanel = new Ext.Panel({
        title:"Instructions", 
        closable:false, 
        autocreate:true,
        layout: 'fit',
        border: false,
        hideBorders: true,
        header: false,
        html: instructions.apply(),
        bodyStyle:"text-align: center; display: table-cell; "+
            "vertical-align: middle; #position: relative; #top: 50%;"
    });

    this.panel = new Ext.Panel({
        id: 'queuepanel',
        region: 'west',
        split: true,
        width: '20%',
        titlebar:false,
        collapsible: true,
        layout: 'card',
        cls: 'queue',
        activeItem: 0,
        items: [this.inspanel, this.tree]
    });


    this.enqueue = enqueue;
    function enqueue(records)
    {
        var play = false;
        if (this.root.childNodes.length == 0) {
            play = true;
            this.panel.getLayout().setActiveItem(1);
        }

        for (i = 0; i < records.length; i++) {
            this.newnode({record:records[i]});
        }

        if(play)
            this.dequeue();
    }

    this.newnode = newnode
    function newnode(config)
    {
        type = config.record.get('type');
        config.queue = this;
        return new typeinfo[type].nodeclass(config);
    }

    this.dequeue = dequeue;
    function dequeue()
    {
        if (this.playing != null) {
            this.playing.remove();
            this.played.push(this.playing.record);
            this.playing = null;
        }
        node = this.root.firstChild;
        if (node) {
            node.dequeue();
        }
        else
            this.fireEvent('stop');
    }

    this.playgridrow = playgridrow
    function playgridrow(grid, songindex, e)
    {
        this.playnow(grid.store.getAt(songindex));
    }

    this.playnow = playnow;
    function playnow(record)
    {
        if (this.playing != null) {
            this.playing.remove();
            this.played.push(this.playing.record);
            this.playing = null;
        }
        else
            this.panel.getLayout().setActiveItem(1);

        new PlayingQueueNode({
            record: record,
            queue: this
        });
    }

    this.prev = prev;
    function prev()
    {
        if (showingprev) {
            this.hideprev();
            show = true;
        }

        if (this.playing)
            this.newnode({
                record: this.playing.record, 
                index: 0,
                replace: true
            });

        var record = this.played.pop();
        if (record) {
            this.playing = new PlayingQueueNode({
                queue: this, 
                record: record, 
                replace: false
            });
        }
        else {
            this.playing = null;
            this.fireEvent('stop');
        }

        if (show)
            this.showprev();
    }

    this.remove = remove;
    function remove(node, checked)
    {
        if (checked) {
            var p = node.parentNode;
            node.remove();
            if (p.update_text)
                p.update_text();
        }
    }

    this.reorder = reorder;
    function reorder(tree, node, oldParent, newParent, index)
    {
        this.fireEvent('reordered');
    }

    this.showprev = showprev
    function showprev()
    {
        showingprev = true;
        for (i = this.played.length-1; i>=this.played.length-5; i--) {
            if (this.played[i]) {
                var newnode = this.newnode({
                    record: this.played[i], 
                    disabled: true,
                    index:0
                });
            }
            else
                break;
        }
    }

    this.hideprev = hideprev
    function hideprev()
    {
        for (i = this.played.length-1 ; i>=this.played.length-5; i--) {
            if (this.played[i]) {
                this.root.firstChild.remove();
            }
            else
                break;
        }
        showingprev = false;
    }

    this.stopreorder = stopreorder
    function stopreorder(tree, node, oldParent, newParent, index)
    {
        if (index == 0)
            return false;
    }

    this.dropped = dropped;
    function dropped(source, e, o)
    {
        alert(o);
    }

    this.tree.on('movenode', this.reorder, this);
    this.tree.on('checkchange', this.remove, this);
    this.tree.on('beforemovenode', this.stopreorder, this);
}

/* Make it so we can fire events */
Ext.extend(PlayQueue, Ext.util.Observable);

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

    QueueNode.superclass.constructor.call(this, this.config);
    /* Prototype for QueueNodes, meant to be extended */
    this.record = config.record;
    this.queue = config.queue;
    this.root = config.root;
    if(this.root == null)
        this.root = this.queue.root;

    if (config.index != null) {
        if (config.replace)
            this.queue.root.replaceChild(this, 
                this.root.item(this.config.index)
            );
        else
            this.root.insertBefore(this,
                this.root.item(this.config.index)
            );
    }
    else
        this.root.appendChild(this);

    this.dequeue = function() {return true;};
    this.update_text = function () {};
}
Ext.extend(QueueNode, Ext.tree.TreeNode);

function SongQueueNode(config)
{
    config.text = config.record.get('title');
    config.checked = false;
    config.leaf = true;
    config.draggable = true;

    SongQueueNode.superclass.constructor.call(this, config);
    this.dequeue = dequeue
    function dequeue()
    {
        //this.config.replace = true;
        new PlayingQueueNode({
            queue: this.queue,
            record: this.record,
            replace: true
        });
    }
}
Ext.extend(SongQueueNode, QueueNode);

function PlayingQueueNode(config)
{
    //config.text = config.record.get('title');
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
    this.queue.playing = this;
    this.queue.fireEvent('playsong', this.record);
}
Ext.extend(PlayingQueueNode, QueueNode);

function AlbumQueueNode(config)
{
    config.text = String.format('{0} ({1}/{1})', 
        config.record.get('album'),
        config.record.get('totaltracks')
    );
    config.draggable = true;
    config.checked = false;
    config.allowDrop = false;
    config.expandable = true;
    config.leaf = false;

    this.songs = new Ext.data.JsonStore({
        url: 'metadata',
        root: 'data',
        sortInfo: {field: 'tracknumber', direction: 'DESC'},
        baseParams: {type:'song', album:config.record.get('albumid')},
        successParameter: 'success',
        autoLoad: false,
        fields: fields
    });
    this.songs_loaded = false;

    AlbumQueueNode.superclass.constructor.call(this, config);

    this.dequeue = dequeue;
    function dequeue()
    {
        /* When an album is dequeued, just get its songs and queue them */
        if (this.songs_loaded) {
            this.queue.playing = new PlayingQueueNode({
                record: this.firstChild.record,
                queue: this.firstChild.queue
            });
            this.firstChild.remove();

            /* now that one of my songs is playing, update myself*/
            this.update_text();
            return true;
        }
        else {
            this.songs.load({
                callback: songs_callback,
                scope: this,
                play: true
            });
            return false
        }
    }

    this.update_text = update_text;
    function update_text()
    {
        this.setText(String.format('{0} ({1}/{2})',
            this.record.get('album'),
            this.childNodes.length,
            this.record.get('totaltracks')
        ));
        if (this.childNodes.length == 0) /* end of album */
            this.remove();
    }

    function on_expand(node)
    {
        if (!this.songs_loaded)
            this.songs.load({
                callback: songs_callback,
                scope: this,
                play: false
            });
    }

    function songs_callback(records, options, success)
    {
        if(!success)
        {
            alert("Something fucked up");
            return;
        }

        this.songs_loaded = true;
        queue_songs.call(this);
        if (options.play){
            this.queue.dequeue();
        }
    }

    function queue_songs()
    {
        this.songs.each(function(record) {
            newnode = new SongQueueNode({
                queue: this.queue, 
                record: record,
                root: this,
                index:0
            });
        }, this);
    }

    this.on('expand', on_expand, this);
}
Ext.extend(AlbumQueueNode, QueueNode);

function ArtistQueueNode(queue, name, record)
{
    ArtistQueueNode.superclass.constructor.call(this, queue, record);
}
Ext.extend(ArtistQueueNode, QueueNode);

