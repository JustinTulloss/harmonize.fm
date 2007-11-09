/* Justin Tulloss
 * 
 * Javascript to manage what's going on with the playqueue
 *  --Largely based off browser class for now
 *
 *  Updated 11/6/07 (r43) to support ExtJS --JMT
 */

function PlayQueue(domObj, dragGroup)
{
    var div = Ext.get(domObj);
    var queue = new Ext.dd.DropTarget(div);
    queue.addToGroup("GridDD"); //This is undocumented, but necessary!

    var instructions = new Ext.Template(
            '<div id="instruction" class="instruction">',
                    'Drag here to add songs',
                    '<br>-OR-<br>',
                    'Hit the <img class="middle" src="/images/enqueue.png" /> button',
            '</div>');

    instructions.overwrite(div);
    clear = true;

    //Let's try a tree instead of a datasource, just for kicks and giggles
    Tree = Ext.tree;
    tree = new Tree.TreePanel(div, {
                animate:true,
                enableDD:true,
                fitToFrame:true,
                rootVisible:false
            });
    root = new Tree.AsyncTreeNode({text:'queue', draggable:false, id:'source'});
    tree.setRootNode(root);

    queue.notifyDrop = dropAction;

    function dropAction(source, e, data)
    {
        data.selections.each(addSelection);
    }

    function addSelection(song) {
        addRow(song.data);
    }
    
    /* Public functions */
    this.addRow = addRow;

    function addRow(newRow)
    {
	    if (clear==true) {
            div.dom.innerHTML="<div id='clearQueue' class='clearQueue'<a href=# onClick='playqueue.clearQueue()'>Clear Queue<\a>";
            tree.render();
            root.expand();
            clear = false;
        }

        nodeConfig = {
            text:newRow.title, 
            id:newRow.title,
            cls: "x-tree-noicon",
            allowDrop: false
        }

        switch(newRow.type) {
            case 'artist':
                addArtist(newRow);
                return;                               
            case 'album':
                nodeConfig.text = newRow.album + " - "+newRow.artist;
                nodeConfig.id = newRow.album;
                break;
            case 'song':
                nodeConfig.text = newRow.title;
                nodeConfig.id = newRow.title;
                nodeConfig.leaf = true;
                break;
            case 'genre':
                addGenre(newRow);
                return;
            case 'friend':
                addFriend(newRow);
                return;
        }

        newNode = new Tree.AsyncTreeNode(nodeConfig);
        root.appendChild(newNode);
    }

    function addArtist(row)
    {
        //request albums by artist asynchronously
        var tmpStore = new Ext.data.JsonStore({
            url: 'player/get_data',
            root: 'data',
            fields: ['album', 'artist']
        });
        tmpStore.load({
            params:{type:'album', artist:row.artist},
            callback: enqueueAlbums,
        });
    }

    function enqueueAlbums(records, options, success)
    {
        if (!success)
            return;
        for (var i = 0; i<records.length; i++) {
            newNode = new Tree.AsyncTreeNode({
                text:records[i].get('album') + " - " + records[i].get('artist'),
                id:records[i].get('album'),
                cls: "x-tree-noicon",
                allowDrop: false
            });
            root.appendChild(newNode);
        }
    }
    
    this.clearQueue = clearQueue;
    function clearQueue()
    {
       var children = root.childNodes;
       while(children.length>0)
       {
         removeSong(children[0]);
       }
    }
    
    this.removeSong = removeSong;
    function removeSong(delSong)
    {
        root.removeChild(delSong);
    }
    
}


