/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 *   > Yeah, that totally worked. This is the primary grid for the app now --JMT
 */

function Browser(fields)
{
    this.addEvents({
        newgrid : true,
        newgridleaf : true,
        newgridbranch : true,
        enqueue : true
    });

    this.actions={
        addtoqueue: function(records) {this.fireEvent('enqueue', records)}
    };
        
    /***** public functions ****/
    this.load = load;
    function load(crumb, params)
    {
        if(crumb.ds==null) {
            crumb.ds = new Ext.data.JsonStore({
                url:'metadata',
                root: 'data',
                successProperty: 'success',
                fields:fields
            });
        }

        /* load as soon as possible so we can get other work done */
        if(params)
            params.type = crumb.type;
        else
            params = {type:crumb.type};
        crumb.ds.load({params:params});

        if (crumb.panel == null) {
            crumb.panel = new Ext.grid.GridPanel({
                ds: crumb.ds,
                cm: typeinfo[crumb.type].cm,
                selModel: new Ext.grid.RowSelectionModel(),
                enableColLock:false,
                enableDragDrop: true,
                loadMask: true,
                autoExpandColumn: 'auto',
                trackMouseOver: false
            });
            crumb.panel.on('render', function(grid) {
                grid.browser = this;
                grid.getView().mainBody.on('mousedown', this.onMouseDown, grid);
            }, this);

            this.fireEvent('newgrid', crumb);
            if (typeinfo[crumb.type].next == 'play')
                this.fireEvent('newgridleaf', crumb);
            else
                this.fireEvent('newgridbranch', crumb);
        }
    }

    /* this is called in the scope of the grid */
    this.onMouseDown = onMouseDown;
    function onMouseDown(e, div)
    {
        /* XXX: Does this loop scale to lots of actions? */
        for (action in this.browser.actions) {
            if (Ext.get(div).hasClass(action)) {
                e.stopEvent(); /* Keep this row from getting selected */
                var records = this.getSelectionModel().getSelections();
                this.browser.actions[action].call(this.browser, records);
            }
        }
    }

    this.recommend = recommend;
    function recommend(type, id)
    {
        var connect = new Ext.data.Connection({
            url:'/player/add_rec',
        });
        connect.request({
            params:{'id':id,
                    'type':type}
        });            
        
    }    
    this.changeColModel = changeColModel;
    function changeColModel(type)
    {
        this.grid.reconfigure(this.ds, typeinfo[type].cm);
        this.grid.getView().fitColumns(true);
    }
}

Ext.extend(Browser, Ext.util.Observable);
