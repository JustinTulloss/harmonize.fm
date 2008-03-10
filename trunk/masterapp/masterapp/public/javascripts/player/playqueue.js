/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *
 *  Updated 11/6/07 (r43) to support ExtJS --JMT
 *  Updated 03/08/08 (r162) to not suck --JMT
 *
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

    var npt = new Ext.Template(
        '<div name="np">',
            '<span id="np-title">{title}</span>',
            '<span id="np-info">{info}</span>',
        '</div>');


    var instructions = new Ext.Template(
            '<div id="instruction" >',
                    'Drag here to add songs',
                    '<br>-OR-<br>',
                    'Hit the <img class="middle" src="/images/enqueue.png" /> button',
            '</div>');

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
        border: false,
        autoHeight: true,
        hideBorders: true,
        header: false,
        cls: 'instruction',
        html: instructions.apply()
    });

    this.panel = new Ext.Panel({
        id: 'queuepanel',
        region: 'west',
        split: true,
        width: '16%',
        titlebar:false,
        collapsible: true,
        layout: 'card',
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
            this.newnode(records[i]);
        }

        if(play)
            this.dequeue();
    }

    this.newnode = newnode
    function newnode(record, index, replace)
    {
        type = record.get('type');
        return new typeinfo[type].nodeclass(this, record, index, replace);
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
        if (node)
            new PlayingQueueNode(this, node.record, true);
        else
            this.fireEvent('stop');
    }

    this.prev = prev;
    function prev()
    {
        if (showingprev) {
            this.hideprev();
            show = true;
        }

        if (this.playing)
            this.newnode(this.playing.record, 0, true)

        var record = this.played.pop();
        if (record) {
            this.playing = new PlayingQueueNode(this, record, false);
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
        if (checked)
            node.remove();
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
                var newnode = this.newnode(this.played[i], 0)
                newnode.disable();
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
function QueueNode(queue, record, index, replace)
{
    QueueNode.superclass.constructor.call(this, this.config);
    /* Prototype for QueueNodes, meant to be extended */
    this.record = record;
    this.queue = queue;

    if (index != null) {
        if (replace)
            this.queue.root.replaceChild(this, this.queue.root.item(index));
        else
            this.queue.root.insertBefore(this,this.queue.root.item(index));
    }
    else
        this.queue.root.appendChild(this);
    this.dequeue = function() {};
}

function SongQueueNode(queue, record, index, replace)
{
    this.config = {
        text: record.get('title'),
        checked: false,
        leaf: true,
        draggable: true
    }

    SongQueueNode.superclass.constructor.call(this, queue, record, index, replace);
}

function PlayingQueueNode(queue, record, replace)
{
    this.config = {
        text: record.get('title'),
        leaf: true,
        draggable: false,
        allowDrop: false,
        allowDrag: false,
        cls: 'nowplaying'
    }

    SongQueueNode.superclass.constructor.call(this, queue, record, 0, replace);
    this.queue.playing = this;
    this.queue.fireEvent('playsong', this.record);
}

function AlbumQueueNode(queue, name, record, config)
{
    AlbumQueueNode.superclass.constructor.call(this, queue, record);
}

function ArtistQueueNode(queue, name, record, config)
{
    ArtistQueueNode.superclass.constructor.call(this, queue, record);
}

Ext.extend(QueueNode, Ext.tree.TreeNode);
Ext.extend(SongQueueNode, QueueNode);
Ext.extend(PlayingQueueNode, QueueNode);
Ext.extend(AlbumQueueNode, QueueNode);
Ext.extend(ArtistQueueNode, QueueNode);
