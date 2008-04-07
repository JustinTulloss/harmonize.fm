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
    config.title = config.record.get('title');
    config.artist = config.record.get('album');
    config.album = config.record.get('artist');
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
                queue: this.firstChild.queue,
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

/* These are the custom UI implementations for our tree. The coding style is
 * taken from the ExtJS library instead of what I've been doing above. This is
 * because this style is cleaner when you're just into overriding existing
 * functions and less into extending the actual functionality. --JMT
 */
PlayingNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    // private
    render : function(bulkRender){
        var n = this.node, a = n.attributes;
        var targetNode = n.parentNode ? 
              n.parentNode.ui.getContainer() : n.ownerTree.innerCt.dom;
        
        if(!this.rendered){
            this.rendered = true;
            this.renderElements(n, a, targetNode, bulkRender);
        }else{
            if(bulkRender === true) {
                targetNode.appendChild(this.wrap);
            }
        }
    },
    // private
    renderElements : function(n, a, targetNode, bulkRender){
        // add some indent caching, this helps performance when rendering a large tree
        this.indentMarkup = n.parentNode ? n.parentNode.ui.getChildIndent() : '';

        var buf = ['<li class="x-tree-node">',
            '<div ext:tree-node-id="',n.id,'" class="np-node x-tree-node-leaf x-unselectable ', a.cls,'" unselectable="on">',
                '<span class="x-tree-node-indent">',this.indentMarkup,"</span>",
                '<div class="np-title">', a.title, '</div>',
                '<div class="np-info">', a.artist, '</div>',
                '<div class="np-info">', a.album, '</div>',
            "</div>",
            '<ul class="x-tree-node-ct" style="display:none;"></ul>',
            "</li>"].join('');

        var nel;
        if(bulkRender !== true && n.nextSibling && (nel = n.nextSibling.ui.getEl())){
            this.wrap = Ext.DomHelper.insertHtml("beforeBegin", nel, buf);
        }else{
            this.wrap = Ext.DomHelper.insertHtml("beforeEnd", targetNode, buf);
        }
        this.elNode = this.wrap.childNodes[0];
    },
    updateExpandIcon : Ext.emptyFn,
});

QueueNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    // private
    render : function(bulkRender){
        var n = this.node, a = n.attributes;
        var targetNode = n.parentNode ? 
              n.parentNode.ui.getContainer() : n.ownerTree.innerCt.dom;
        
        if(!this.rendered){
            this.rendered = true;

            this.renderElements(n, a, targetNode, bulkRender);

            if(a.qtip){
               if(this.textNode.setAttributeNS){
                   this.textNode.setAttributeNS("ext", "qtip", a.qtip);
                   if(a.qtipTitle){
                       this.textNode.setAttributeNS("ext", "qtitle", a.qtipTitle);
                   }
               }else{
                   this.textNode.setAttribute("ext:qtip", a.qtip);
                   if(a.qtipTitle){
                       this.textNode.setAttribute("ext:qtitle", a.qtipTitle);
                   }
               } 
            }else if(a.qtipCfg){
                a.qtipCfg.target = Ext.id(this.textNode);
                Ext.QuickTips.register(a.qtipCfg);
            }
            this.initEvents();
        }else{
            if(bulkRender === true) {
                targetNode.appendChild(this.wrap);
            }
        }
    },

    // private
    renderElements : function(n, a, targetNode, bulkRender){
        // add some indent caching, this helps performance when rendering a large tree
        this.indentMarkup = n.parentNode ? n.parentNode.ui.getChildIndent() : '';

        var cb = typeof a.checked == 'boolean';

        var href = a.href ? a.href : Ext.isGecko ? "" : "#";
        var buf = ['<li class="x-tree-node"><div ext:tree-node-id="',n.id,'" class="x-tree-node-el x-tree-node-leaf x-unselectable ', a.cls,'" unselectable="on">',
            '<span class="x-tree-node-indent">',this.indentMarkup,"</span>",
            '<a hidefocus="on" class="x-tree-node-anchor" href="',href,'" tabIndex="1" ',
             a.hrefTarget ? ' target="'+a.hrefTarget+'"' : "", '><span unselectable="on">',n.text,"</span></a>",
            cb ? ('<input class="x-tree-node-cb" type="checkbox" ' + (a.checked ? 'checked="checked" />' : '/>')) : ''
            ,"</div>",
            '<ul class="x-tree-node-ct" style="display:none;"></ul>',
            "</li>"].join('');

        var nel;
        if(bulkRender !== true && n.nextSibling && (nel = n.nextSibling.ui.getEl())){
            this.wrap = Ext.DomHelper.insertHtml("beforeBegin", nel, buf);
        }else{
            this.wrap = Ext.DomHelper.insertHtml("beforeEnd", targetNode, buf);
        }
        
        this.elNode = this.wrap.childNodes[0];
        this.ctNode = this.wrap.childNodes[1];
        var cs = this.elNode.childNodes;
        if(cb){
            this.checkbox = cs[2];
        }
    },

    //private
    getDDHandles : function(){
        return [this.elNode];
    },

    // private
    getDDRepairXY : function(){
        return Ext.lib.Dom.getXY(this.elNode);
    },
    updateExpandIcon : Ext.emptyFn, /* TODO: Fill this in for albums */
});
