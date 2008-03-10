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

    this.addEvents({
        newsong : true,
        reordered : true
    });

    var npt = new Ext.Template(
        '<div name="np">',
            '<span id="np-title">{title}</span>',
            '<span id="np-info">{info}</span>',
        '</div>');


    var instructions = new Ext.Template(
            '<div id="instruction" class="instruction">',
                    'Drag here to add songs',
                    '<br>-OR-<br>',
                    'Hit the <img class="middle" src="/images/enqueue.png" /> button',
            '</div>');

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
        if (this.root.childNodes.length == 0)
            this.panel.getLayout().setActiveItem(1);

        for (i = 0; i < records.length; i++) {
            type = records[i].get('type');
            new typeinfo[type].nodeclass(this, records[i]);
        }
    }

    this.dequeue = dequeue;
    function dequeue(record)
    {
    }

    this.reorder = reorder;
    function reorder(tree, node, oldParent, newParent, index)
    {
        this.fireEvent('reordered');
    }

    this.dropped = dropped;
    function dropped(source, e, o)
    {
        alert(o);
    }

    this.tree.on('movenode', this.reorder, this);

}

/* Make it so we can fire events */
Ext.extend(PlayQueue, Ext.util.Observable);

/* A node for a queue. This mostly just builds the treenode, but it also
 * needs to know how to manipulate that node when things happen. Like when it's
 * being prefetched or when it's time for this node to be played. It's all quite
 * complex.
 */
function QueueNode(queue, record)
{
    QueueNode.superclass.constructor.call(this, this.config);
    /* Prototype for QueueNodes, meant to be extended */
    this.record = record;
    this.queue = queue;

    this.queue.root.appendChild(this);
}

function SongQueueNode(queue, record)
{
    this.config = {
        text: record.get('title'),
        checked: false,
        leaf: true,
        draggable: true
    }

    SongQueueNode.superclass.constructor.call(this, queue, record);
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
Ext.extend(AlbumQueueNode, QueueNode);
Ext.extend(ArtistQueueNode, QueueNode);
