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
        "newsong" : true
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

    this.root = new Ext.tree.TreeNode({text:'root', expanded:true});
    this.tree = new Ext.tree.TreePanel({
        root: this.root
    });

    this.enqueue = enqueue;
    function enqueue(records)
    {
        for (i = 0; i < records.length; i++) {
            type = records[i].get('type');
            typeinfo[type].enqueuefxn.call(this, records[i]);
        }
    }

    this.dequeue = dequeue;
    function dequeue(record)
    {
        type = record.get('type')
        typeinfo[type].dequeuefxn.call(this, record);
    }

}

//Make it so we can fire events
Ext.extend(PlayQueue, Ext.util.Observable);

/* A node for a queue. This mostly just builds the treenode, but it also
   needs to know how to manipulate that node when things happen. Like when it's
   being prefetched or when it's time for this node to be played. It's all quite
   complex.
*/
function QueueNode(name, record, config)
{
    /* set options we know we like here, but otherwise use the type defined config*/
    config.draggable = true;
    config.text = name;

    this.treenode = new Ext.tree.TreeNode(config);
    this.record = record;
}


