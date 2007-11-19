/* Justin Tulloss
 *
 * This is for managing where we are in the world of musical views
 */

function BcEntry(type, value)
{
    this.type = type;
    this.value = value;
}

/* BreadCrumb object
 * Parameters:
 *  DomObj - the div the breadcrumb lives in
 */
function BreadCrumb(domObj, link_action)
{
    var Dom = YAHOO.util.Dom;
    var bclist = new Array(new BcEntry("home"));
    var current = 0;
    var div = Dom.get(domObj);
    //this.link_action = link_action;
    this.link_action = jump_to;

    /* mapping of types to display values */
    colMap = {
        home:'Home', 
        artist:'Artists',
        album:'Album',
        songs:'Songs',
        friend:'Friends',
        genre:'Genres'
    };


    /*public functions*/
    this.current_view = current_view;
    this.update = update;
    this.descend = descend;
    this.ascend = ascend;
    this.jump_to = jump_to;
    this.create_query = create_query;

    function current_view()
    {
        return bclist[current].type;
    }

    function descend(curvalue, newFilter)
    {
        bclist[current].value = curvalue;
        current++;
        bclist.splice(current, bclist.length-current, newFilter);
        return update();
    }

    function ascend()
    {
        current--;
        return update();
    }

    function jump_to(type)
    {
	    for (var i=0;i<bclist.length;i++) {
            if (bclist[i].type == type) {
                current = i;
                bclist[i].vale = null;
            }
        }
        return update();
    }

    function update()
    {
        update_div();
        return create_params();
    }

    function update_div()
    {
        /* For now, clear and rebuild everytime. It should be cheaper than
         * fetching the data from the server anyway, so who cares?
         */
        div.innerHTML = "";
        for (var i=0; i<bclist.length; i++) {
            newId = "bc_"+bclist[i].type;

            if (bclist[i].value==null)
                value = colMap[bclist[i].type];
            else
                value = bclist[i].value;

           if (current == i) {
                div.innerHTML += "<div class='bc bc_current' id="+newId+">" + 
                    value +
                "</div>";
            }
            else {
                div.innerHTML += "<div class='bc' id="+newId+">" + 
                    "<a class='bc_link' href='#' onclick=jump_to('"+bclist[i].type+"')>"+
                        value + 
                    "</a>"
                "</div>";
            }
            if (i != bclist.length-1) {
                div.innerHTML += "<div class='bc bc_separator'>-></div>"
            }

        }
    }


    /* Looks at where we are and creates a url-query string for that data.
     * ex: artist=Radiohead&album=Kid%20A (does not return a beginning ?)
     */
    function create_query()
    {
        qrystr = "";
        for (var i=0; i<bclist.length; i++) {
            if (i>0)
                qrystr += "&";
            if (bclist[i].value != null)
                qrystr += escape(bclist[i].type)+"="+escape(bclist[i].value);
        }
        return qrystr;
    }

    function create_params()
    {
        params = {type:null};
        for(var i=0; i<current; i++) {
            if(bclist[i].value != null)
                params[bclist[i].type] = bclist[i].value;
        }
        return params;
    }

}

