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
            div.dom.innerHTML="";
            tree.render();
            root.expand();
            clear = false;
        }
        newNode = new Tree.AsyncTreeNode({
            text:newRow.title, 
            id:newRow.title,
	    allowDrop: false
        });
        root.appendChild(newNode);
    }

}


