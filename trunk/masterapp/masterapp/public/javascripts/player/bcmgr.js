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

    if (qryvalue)
        this.qryvalue = qryvalue
    else
        this.qryvalue = value;

    if (qrytype)
        this.qrytype = qrytype
    else
        this.qrytype = type;
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
    var crumb = new Ext.Template(
        '<div class="bc" name="{id}">',
            '<a class="bc_link" href="#{ajaxlink}">{name}</a>',
        '</div>'
    );
    var active_crumb = new Ext.Template(
        '<div class="bc bc_current" name="{id}">',
            '<span>{name}</span>',
        '</div>'
    );
    var separator = new Ext.Template("<div class='bc bc_separator'>-></div>");

    crumb = crumb.compile(); /* Way fast */
    active_crumb = active_crumb.compile();

    this.addEvents({
        "bcupdate" : true
    });

    /*public functions*/
    this.current_view = current_view;
    this.update = update;
    this.update_div = update_div;
    this.descend = descend;
    this.ascend = ascend;
    this.jump_to = jump_to;

    this.update()

    function current_view()
    {
        return bclist[current].type;
    }

    function descend(curvalue, qryvalue, newFilter)
    {
        bclist[current].value = curvalue;
        bclist[current].qryvalue = qryvalue;

        current++;
        bclist.splice(current, bclist.length-current, newFilter);
        return this.update();
    }

    function ascend()
    {
        current--;
        return this.update();
    }

    function jump_to(e)
    {
        var el = e.getTarget(null, null, true);
        var thelist = bclist;
	    for (var i=0;i<bclist.length;i++) {
            if (bclist[i].el.contains(el)) {
                current = i;
                this.fireEvent('bcupdate', bclist[i])
            }
        }
        return this.update();
    }

    function update()
    {
        this.update_div();
        return create_params();
    }

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
                newEl = active_crumb.append(div, {id:newId, name:value}, true);
            }
            else {
                newEl = crumb.append(div, {id:newId, name:value}, true);
                newEl.on('click',this.jump_to, this);
            }
            bclist[i].el = newEl;
            bclist[i].id = newEl.id;

            if (i != bclist.length-1)
                separator.append(div);
        }
    }

    function create_params()
    {
        params = {type:null};
        for(var i=0; i<current; i++) {
            if(bclist[i].qryvalue != null)
                params[bclist[i].qrytype] = bclist[i].qryvalue;
        }
        return params;
    }

}

Ext.extend(BreadCrumb, Ext.util.Observable);
