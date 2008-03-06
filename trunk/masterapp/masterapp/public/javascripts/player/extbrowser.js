/* Justin Tulloss
 *
 *
 * Experimenting with replacing the YUI datatable with an extjs one
 *   > Yeah, that totally worked. This is the primary grid for the app now --JMT
 */

function Browser(fields)
{
    this.addEvents({
        "newgrid" : true,
        "newgridleaf" : true,
        "newgridbranch" : true
    });
        
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
            this.fireEvent('newgrid', crumb);
            if (typeinfo[crumb.type].next == 'play')
                this.fireEvent('newgridleaf', crumb);
            else
                this.fireEvent('newgridbranch', crumb);
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
