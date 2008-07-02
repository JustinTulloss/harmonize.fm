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
 * 06/01/2008 - Updated to use the location instead of jump_to and other such
 *              ugliness --JMT
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
	if (this == window) alert('new not used!');
	var my = this;

    var bclist = [];
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
    var separator = new Ext.Template(
			"<div class='bc bc_separator'>&nbsp;>&nbsp;</div>");

    t_crumb = t_crumb.compile(); /* Makes this template way fast */
    t_active_crumb = t_active_crumb.compile();

    this.addEvents({
        'bcupdate' : true,
        'newfilter' : true,
        'chgstatus' : true
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
        if (clickedinfo.qryindex)
            bclist[current].qryvalue = row.get(clickedinfo.qryindex);
        else
            bclist[current].qryvalue = row.get(clickedtype);
        
        /* Call the type's defined next action */
        clickedinfo.next(row, this);
    }

    this.addbreadcrumb = addbreadcrumb;
    function addbreadcrumb(crumb)
    {
        current++;

        /* removes everything after new current and adds on newcrumb */
        bclist.splice(current, bclist.length-current, crumb);
        this.update_div();
        var params = create_params(bclist[current]);
        var url = build_bc_url(bclist.length-1);
        urlm.goto_url(url);
        bclist[current].url = url;
    }

    function build_bc_url(index){
        urllist = ['/bc'];
        for (var i=0; i < index; i++) {
            part = bclist[i].type;
            if (bclist[i].qryvalue)
                part += '='+bclist[i].qryvalue;
            urllist.push(part);
        }
        urllist.push(bclist[index].type);
        return urllist.join('/');
    }


    my.load_url = function(url) { 
        build_bc(url);
    }

    function build_bc(url) {
        var parts = url.split('/')
        var params = {};
        var param;
        var splice = false;
        for (var i =0; i<parts.length; i++) {
            param = parts[i].split('=');
            if (param.length == 2) {
                params[param[0]] = param[1];
            }
            if (bclist[i]) {
                if (bclist[i].type != param[0]) {
                    /* this is not a currently loaded bc */
                    bclist[i] = new BcEntry(param[0], null, param[0], param[1]);
                    bclist[i].url = build_bc_url(i);
                    splice = true;
                }
            }
            else
                bclist[i] = new BcEntry(param[0], null, param[0], param[1]);
                bclist[i].url = build_bc_url(i);
            current = i;
        }
        if (splice)
            bclist.splice(current+1, bclist.length-current+1);
        my.update_div();
        my.fireEvent('bcupdate', bclist[current], params);
        if (!bclist[current].panel)
            my.fireEvent('newfilter', bclist[current], params);
    }

    this.update_current_div = function(crumb, oldcrumb) {
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
        crumb.el.un('click', jump_to)
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
            t_crumb.overwrite(crumb.el, {
                id:crumb.name, 
                name:value, 
                ajaxlink: crumb.url
            });
        }
    }

    my.update_div = update_div;
    function update_div()
    {
        /* For now, clear and rebuild everytime. It should be cheaper than
         * fetching the data from the server anyway, so who cares?
         */
        div.update('');
        for (var i=0; i<bclist.length; i++) {
            var curr_bc = bclist[i];
            var newId = "bc_"+bclist[i].type;
            var newEl = null;

            if (bclist[i].value==null)
                value = typeinfo[bclist[i].type].display;
            else
                value = bclist[i].value;

            if (current == i) {
                newEl = t_active_crumb.append(div, {id:newId, name:value},true);
            }
            else {
                newEl = t_crumb.append(div, {
                    id:newId, 
                    name:value,
                    ajaxlink: bclist[i].url
                }, true);
            }
            bclist[i].el = newEl;
            bclist[i].id = newEl.id;
            bclist[i].name = newId;

            if (i != bclist.length-1)
                separator.append(div);
        }
    }

    my.update_div();

    function create_params(current_crumb)
    {
        var params = {};
        for(var i=0; i<current; i++) {
            if(bclist[i].qryvalue != null)
                params[bclist[i].qrytype] = bclist[i].qryvalue;
        }
        return params;
    }
    
    my.reload = function() {
        my.fireEvent('chgstatus', 'Loading...');
        if (bclist[current])
            bclist[current].ds.lastOptions.params.limit = null;
            bclist[current].ds.lastOptions.params.start = null;
            bclist[current].ds.reload({
                add: false,
                callback: function(r, options, success){
                    my.fireEvent('chgstatus', null);
                }
            });
    }
}

Ext.extend(BreadCrumb, Ext.util.Observable);
