/* Justin Tulloss
 * 05/31/08
 *
 * Takes care of javascript present on a profile page.
 */

function profile_factory(url) {
    var newprofile = new Profile(url);
    return newprofile.panel;
}

function Profile(id)
{
    var my = this;
    my.panel = new Ext.Panel({
        layout: 'column',
        autoScroll: true,
        nocrumb: true,
        items: [{
            autoLoad: 'people/profile_body/'+id,
            layout: 'fit',
            columnWidth: 1
        },{
            autoLoad: 'people/profile_right/'+id,
            layout:'fit',
            width: 220
        }],
    });

    urlmanager.register_handlers([
        ['/profile_comments/', view_comments],
    ]);

    my.go = function(url) {
        alert(url);
    }
    function view_comments(spotlightid)
    {
        alert(spotlightid);
    }
}
