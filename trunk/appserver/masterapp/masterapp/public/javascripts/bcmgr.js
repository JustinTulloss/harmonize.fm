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
    var bclist = new Array(new BcEntry("artist", "Radiohead"), new BcEntry("album"));
    var current = 0;
    var div = Dom.get(domObj);
    //this.link_action = link_action;
    this.link_action = jump_to;

    /*public functions*/
    this.update = update;
    this.descend = descend;
    this.ascend = ascend;
    this.jump_to = jump_to;
    this.create_query = create_query;

    function descend(newFilter)
    {
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
            if (bclist[i].type == type)
                current = i;
        }
        return update();
    }

    function update()
    {
        update_div();
        return create_query();
    }

    function update_div()
    {
        /* For now, clear and rebuild everytime. It should be cheaper than
         * fetching the data from the server anyway, so who cares?
         */
        div.innerHTML = "";
        for (var i=0; i<bclist.length; i++) {
            newId = "bc_"+bclist[i].type;
           if (current == i) {
                div.innerHTML += "<div class='bc bc_current' id="+newId+">" + 
                    bclist[i].value + 
                "</div>";
            }
            else {
                div.innerHTML += "<div class='bc bc_link' id="+newId+">" + 
                    "<a href= 'javascript:jump_to(\'artist\')'>"+
                        bclist[i].value + 
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
}

