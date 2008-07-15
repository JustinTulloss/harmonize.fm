/* Justin Tulloss
 *
 * This is for managing where we are in the world of musical views.
 *
 * 03/03/2008 - Starting a cleanup effort to:
 *              1. Pull apart application look and behavior
 *              2. Put more functionality in here.
 *              --JMT
 * 06/01/2008 - Updated to use the location instead of jump_to and other such
 *              ugliness --JMT
 * 07/11/2008 - Began a fairly major rework
 */

/* An entry of data in the breadcrumb. Generally what you display and what
 * you query for are the same, but in the case of friends and albums, we
 * query for IDs that aren't presented anywhere. So, we allow you to
 * differentiate between what is displayed and what you want to query for.
 */

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
    var current = -1;
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
        'chgstatus' : true
    });

    /* Entries */
    my.Crumb = function(config)
    {
        if (this === window)
            alert('Use new to create a new crumb');
        var my = this;
        my.type = config.type;
        my.value = config.value;
        my.el = null;
        my.id = null;
        my.view = null;
        my.url = null;

        Ext.apply(my, config);

        my.qrytype = config.type;

        if (!my.qryvalue)
            my.qryvalue = config.value;

    }

    /*public functions*/
    my.current_view = function() {
        return bclist[current];
    }

    my.load_url = function(url) {
        //clear search
        viewmgr.search_field.reset();

        if (url.indexOf('?') != -1) {
            //this means there is a variable somewhere
            url = url.split('?');
            location.vars = url[1];
            url = url[0];
        }
        var parts = url.split('/')
        var params = {};
        var param = null;
        var splice = false;
        var i;
        for (i=0; i<parts.length; i++) {
            param = parts[i].split('=');
            var type = param[0];
            var value = null;
            if (param.length == 2) {
                value = param[1];
                params[type] = value;
            }

            function create_bc() {
                bclist[i] = new my.Crumb({
                    type: type,
                    qryvalue: value
                });
                bclist[i].viewurl = typeinfo[bclist[i].type].urlfunc(bclist[i]);
            }

            if (bclist[i] && !splice) {
                if (bclist[i].type != type){
                    create_bc();
                    splice = true;
                }
                if (value && bclist[i].qryvalue != value) {
                    bclist[i].qryvalue = value;
                    splice = true;
                }
            }
            else {
                create_bc();
            }
            current = i;
        }
        if (splice)
            bclist.splice(current+1, bclist.length-current+1);

        if (!bclist[current].panel)
            Hfm.browser.load(bclist[current], params);
        else{
            Hfm.view.set_panel(bclist[current], params);
            update_div();
        }
    }

    my.add = function(config) {
        var crumb = config.crumb;
        if (config.index)
            current = config.index;
        else
            current++;

        /* removes everything after new current and adds on newcrumb */
        bclist.splice(current, bclist.length-current, crumb);
        if (config.update)
            update_div();
        var params = create_params(bclist[current]);
        var url = typeinfo[crumb.type].urlfunc(crumb);
        bclist[current].viewurl = url;
        return url;
    }

    my.build_url = function(crumb){
        var urllist = ['/browse'];
        var i = 0;
        var itercrumb = bclist[0];
        while (itercrumb != crumb) {
            part = itercrumb.type;
            if (itercrumb.qryvalue)
                part += '='+itercrumb.qryvalue;
            urllist.push(part);
            i++;
            itercrumb = bclist[i];
        }
        urllist.push(crumb.type);
        return urllist.join('/');
    }

    my.update_current_div = function(crumb, oldcrumb) {
        setup_current_div(crumb);
        if (oldcrumb)
            setup_inactive_div(oldcrumb);
    }

    my.update_display_values = function(row) {
        for (var i = 0; i<bclist.length-1; i++) {
            crumb = bclist[i];
            labelcrumb = bclist[i+1];
            if (crumb.type != row.get('type')) {
                newvalue = row.get(typeinfo[crumb.type].lblindex)
                if (newvalue && labelcrumb.value != newvalue)
                    labelcrumb.value = newvalue;
            }
        }
        update_div();
    }

    function setup_current_div(crumb)
    {
        /* Make new current not a link */
        if (crumb.value==null)
            value = typeinfo[crumb.type].display;
        else
            value = crumb.value;
        t_active_crumb.overwrite(crumb.el, {id:crumb.name, name:value});
    }

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
                ajaxlink: crumb.viewurl
            });
        }
    }

    my.update = function(newcurrent) {
        if (newcurrent)
            current = newcurrent;
        update_div()
    }

    function update_div()
    {
        /* For now, clear and rebuild everytime. It should be cheaper than
         * fetching the data from the server anyway, so who cares?
         */
        div = Ext.fly('breadcrumb');
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
                    ajaxlink: bclist[i].viewurl
                }, true);
            }
            bclist[i].el = newEl;
            bclist[i].id = newEl.id;
            bclist[i].name = newId;

            if (i != bclist.length-1)
                separator.append(div);
        }
    };

    //update_div();

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

    my.is_friends_library = function() {
        if (bclist[0] == null) return false;        
        if (bclist[0].type == 'friend') return true;
        else return false;
    }
}

Ext.extend(BreadCrumb, Ext.util.Observable);

Hfm.breadcrumb = new BreadCrumb();
