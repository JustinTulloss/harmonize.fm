/* Justin Tulloss
 *
 * This is for managing where we are in the world of musical views.
 *
 * TODO: Clean this up a bit. Right now this is very closely tied to the
 * HTML breadcrumb itself while tangling in storage for what parameters are
 * currently in use
 *
 * 03/03/2008 - Starting a cleanup effort to:
 *              1. Pull apart application look and behavior
 *              2. Put more functionality in here.
 *              --JMT
 */

/* An entry of data in the breadcrumb. Generally what you display and what
 * you query for are the same, but in the case of friends and albums, we
 * query for IDs that aren't presented anywhere. So, we allow you to
 * differentiate between what is displayed and what you want to query for.
 */
function BcEntry(type, value, qrytype, qryvalue)
{
    this.type = type;
    this.value = value;
    this.el = null;
    this.id = null;
    this.view = null;

    if (qrytype)
        this.qrytype = qrytype
    else
        this.qrytype = type;

    if (qryvalue)
        this.qryvalue = qryvalue
    else
        this.qryvalue = value;
}

/* BreadCrumb object
 *
 * Figures out what filters have been applied and maintains the actual
 * HTML breadcrumb
 */
function BreadCrumb()
{
    var bclist = new Array(new BcEntry("home"));
    var current = 0;
    var div = Ext.get("breadcrumb"); /* XXX: Hard coded badness */
    var t_crumb = new Ext.Template(
        '<div class="bc" name="{id}">',
            '<a class="bc_link" href="#{ajaxlink}">{name}</a>',
        '</div>'
    );
    var t_active_crumb = new Ext.Template(
        '<div class="bc bc_current" name="{id}">',
            '<span>{name}</span>',
        '</div>'
    );
    var separator = new Ext.Template("<div class='bc bc_separator'>-></div>");

    t_crumb = t_crumb.compile(); /* Makes this template way fast */
    t_active_crumb = t_active_crumb.compile();

    this.addEvents({
        'bcupdate' : true,
        'newfilter' : true
    });


    /*public functions*/
    this.current_view = current_view;
    function current_view()
    {
        return bclist[current];
    }

    this.descend = descend;
    function descend(grid, rowindex, e)
    {
        var row = grid.store.getAt(rowindex);
        var clickedtype = row.get('type');
        var clickedinfo = typeinfo[clickedtype];

        /* Change the old crumb to show updated values */
        bclist[current].value = row.get(clickedtype);
        if (clickedinfo.qry)
            bclist[current].qryvalue = row.get(clickedinfo.qry);
        else
            bclist[current].qryvalue = row.get(clickedtype);
        
        /* Make new crumb describing what you're looking at */
        var newtype = typeinfo[clickedinfo.next]
        var newcrumb = new BcEntry(
            clickedinfo.next, 
            newtype.display, 
            clickedinfo.next
        );

        current++;
        /* removes everything after new current and adds on newcrumb */
        bclist.splice(current, bclist.length-current, newcrumb);
        this.update_div();
        params = create_params(bclist[current]);
        this.fireEvent('bcupdate', bclist[current], params);
        this.fireEvent('newfilter', bclist[current], params);
    }

    this.go = go;
    /* This function goes 1 past home to a fresh, unfiltered type */
    function go(type)
    {
        newtype = typeinfo[type]
        newcrumb = new BcEntry(type, newtype.display, type);
        current = 1;
        bclist.splice(current, bclist.length-current, newcrumb);
        this.update_div();
        this.fireEvent('bcupdate', bclist[current], null);
        this.fireEvent('newfilter', bclist[current], null);
    }

    this.go_home = go_home
    function go_home()
    {
        current = 0;
        bclist.splice(1, bclist.length-1);
        this.update_div();
        this.fireEvent('bcupdate', bclist[current]);
    }

    this.jump_to = jump_to;
    function jump_to(e)
    {
        var el = e.getTarget(null, null, true);
        var thelist = bclist;
	    for (var i=0;i<bclist.length;i++) {
            if (bclist[i].el.contains(el)) {
                this.update_current_div(bclist[i], bclist[current]);
                current = i;
                params = create_params(bclist[current]);
                this.fireEvent('bcupdate', bclist[current], params);
            }
        }

    }

    this.update_current_div = update_current_div;
    function update_current_div(crumb, oldcrumb) {
        this.setup_current_div(crumb);
        if (oldcrumb)
            this.setup_inactive_div(oldcrumb);

    }

    this.setup_current_div = setup_current_div;
    function setup_current_div(crumb)
    {
        /* Make new current not a link */
        if (crumb.value==null)
            value = typeinfo[crumb.type].display;
        else
            value = crumb.value;
        crumb.el.un('click', this.jump_to)
        t_active_crumb.overwrite(crumb.el, {id:crumb.name, name:value});
    }

    this.setup_inactive_div = setup_inactive_div;
    function setup_inactive_div(crumb)
    {
        /* Make inactive div a link */
        if (crumb != null) {
            if (crumb.value==null)
                value = typeinfo[crumb.type].display;
            else
                value = crumb.value;
            t_crumb.overwrite(crumb.el, {id:crumb.name, name:value});
            crumb.el.on('click',this.jump_to, this);
        }
    }

    this.update_div = update_div;
    function update_div()
    {
        /* For now, clear and rebuild everytime. It should be cheaper than
         * fetching the data from the server anyway, so who cares?
         */
        div.update('');
        for (var i=0; i<bclist.length; i++) {
            var newId = "bc_"+bclist[i].type;
            var newEl = null;

            if (bclist[i].value==null)
                value = typeinfo[bclist[i].type].display;
            else
                value = bclist[i].value;

            if (current == i) {
                newEl = t_active_crumb.append(div, {id:newId, name:value}, true);
            }
            else {
                newEl = t_crumb.append(div, {id:newId, name:value}, true);
                newEl.on('click',this.jump_to, this);
            }
            bclist[i].el = newEl;
            bclist[i].id = newEl.id;
            bclist[i].name = newId;

            if (i != bclist.length-1)
                separator.append(div);
        }
    }

    this.update_div();

    function create_params(current_crumb)
    {
        params = {};
        for(var i=0; i<current; i++) {
            if(bclist[i].qryvalue != null)
                params[bclist[i].qrytype] = bclist[i].qryvalue;
        }
        return params;
    }

}

Ext.extend(BreadCrumb, Ext.util.Observable);
