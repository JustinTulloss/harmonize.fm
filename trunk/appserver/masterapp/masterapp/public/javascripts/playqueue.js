/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *  --Largely based off browser class for now
 *
 *  Updated 11/6/07 (r43) to support ExtJS --JMT
 *
 */

function PlayQueue(domObj, dragGroup, fields)
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

	
    clear = true;

    //This stores every song that's ever been put in the queue.
    //The tree manages the look, this manages the actual data
    queueStore = new Ext.data.SimpleStore({fields:fields});

    viewData = new Ext.util.MixedCollection();

    this.queue = queueStore;
    var nowplaying = -1;

    Tree = Ext.tree;
    this.tree = new Tree.TreePanel({
                animate:true,
                enableDD:true,
                ddGroup:'GridDD',
                ddScroll: true,
                fitToContainer:true,
                rootVisible:false,
				containerScroll:true,
                fitToFrame: true,
                ctCls: 'queue-container',
                dropConfig: {
                    allowContainerDrop: true,
                    ddGroup: 'GridDD'
                }
            });
    root = new Tree.AsyncTreeNode({
        text:'queue', 
        draggable:false, 
        id:'source'
    });
    this.tree.setRootNode(root);

    function newNode(title, id, leaf)
    {
        nodeConfig = {
            text:title, 
            id:id,
            leaf: leaf,
            cls: "x-tree-noicon",
            allowDrop: false
        }
        var nn = new Tree.AsyncTreeNode(nodeConfig);
        return nn;
    }
        
    function dropAction(source, e, data)
    {
        for (var i =0; i<data.selections.length; i++) {
            addRecord(data.selections[i]);
        }
    }

    function makeViewId(records, insert)
    {
        if (insert)
            queueStore.insert(0,records);
        else
            queueStore.add(records);

        var newViewNode = {
            start: queueStore.getAt(queueStore.getCount()-records.length),
            end: queueStore.getAt(queueStore.getCount()-1)
        };

        id = Ext.id(); 
        if (insert)
            viewData.insert(0, id, newViewNode);
        else
            viewData.add(id, newViewNode);

        return id;
    }


    this.getTree = getTree;
    function getTree()
    {
        return tree;
    }

    this.addRecord = addRecord;
    function addRecord(newRow)
    {
	    if (clear==true) {
            //div.dom.innerHTML="";
            this.tree.render();
            root.expand();
            clear = false;
        }

        switch(newRow.get('type')) {
            case 'artist':
                addArtist(newRow);
                return;
            case 'album':
                addAlbum(newRow);
                return;
            case 'song':
                var idx = makeViewId([newRow]);
                var nn = newNode(newRow.get('title'),idx , true);
                root.appendChild(nn);
                return;
            case 'genre':
                addGenre(newRow);
                return;
            case 'friend':
                addFriend(newRow);
                return;
        }

    }

    function addArtist(row)
    {
        //request albums by artist asynchronously
        var tmpStore = new Ext.data.JsonStore({
            url: 'player/get_data',
            root: 'data',
            fields: fields
        });
        tmpStore.load({
            params:{type:'album', artist:row.get('artist')},
            callback: enqueueAlbums,
        });
    }

    function enqueueAlbums(records, options, success)
    {
        if (!success)
            return;

        for (var i=0; i<records.length; i++)
            addAlbum(records[i]);
    }

    function addAlbum(row)
    {
        var tmpStore = new Ext.data.JsonStore({
            url: 'player/get_data',
            root: 'data',
            fields: fields
        });

        tmpStore.load({
            params:{type:'song', artist:row.get('artist'), album:row.get('album')},
            callback: enqueueAlbum,
        });
    }

    function enqueueAlbum(records, options, success)
    {
        if (!success)
            return;
        var idx = makeViewId(records);
        var nn = newNode(records[0].get('album') + ' - '+ records[0].get('artist'), idx, false);
        root.appendChild(nn);
    }

	this.tree.on("append", addDeleteButton);
	function addDeleteButton(theTree, theParent, theNode, index)
	{
		
		theNode.setText(theNode.text+"<a href=# onclick='playqueue.removeByID(\""+theNode.id+"\")'> <img src= /images/song_remove.png></a>");
	}
    
    this.clearQueue = clearQueue;
    function clearQueue()
    {
        while(root.childNodes.length>0)
            removeNode(root.childNodes[0]);
        //I love the consistency of this API
        queueStore.removeAll();
        viewData.clear();
    }
    
    this.setNowPlaying = setNowPlaying;
    function setNowPlaying(record)
    {
        npt.overwrite('now-playing', {
                title:record.get("title"), 
                info:record.get("artist")+' - '+record.get("album") 
            });
        this.fireEvent('playsong', record);
    }

    this.removeNode = removeNode;
    function removeNode(delSong)
    {
        if(delSong.nextSibling==null) {
            clear = true;
            //instructions.overwrite(div);
        }
        var queueEntries = viewData.key(delSong.id);
        var start = queueStore.indexOf(queueEntries.start);
        var end = queueStore.indexOf(queueEntries.end);
        delRecords = queueStore.getRange(start, end);
        for (var i = 0; i<delRecords.length; i++)
            queueStore.remove(delRecords[i]);

        viewData.removeKey(delSong.id);
        root.removeChild(delSong);
    }

    function removeThisSong()
	{
        removeNode(this);
	}
	                                             
	this.removeByID = removeByID;
	function removeByID(id)
	{
        delNode = this.tree.getNodeById(id);
        removeNode(delNode);
	}
   
    this.nextsong = nextsong;
    function nextsong(e) 
    {
        if (queueStore.getCount<1)
            return;

        nowplaying++;
        if (nowplaying > queueStore.indexOf(viewData.itemAt(0).end)) {
            viewData.removeAt(0);
            root.removeChild(root.firstChild);
        }

        var npr = queueStore.getAt(nowplaying)
        this.setNowPlaying(npr);
    }

    this.backsong = backsong;
    function backsong(e)
    {
        if (queueStore.getCount()>root.childNodes.length) {
            var record = queueStore.getAt(nowplaying);
            nowplaying--;
            npr = queueStore.getAt(nowplaying);
            this.setNowPlaying(npr);
            if (nowplaying < queueStore.indexOf(viewData.itemAt(0).start)) {
                key = makeViewId([record], true);
                var nn = newNode(record.get('title'), key, true);
                root.insertBefore(nn, root.firstChild);
            }
        }
    }
}

//Make it so we can fire events
Ext.extend(PlayQueue, Ext.util.Observable);


