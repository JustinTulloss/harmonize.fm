/* Justin Tulloss
 * 03/04/2008
 *
 * In an effort to avoid this becoming a catchall for whatever functionality
 * we can't think to put anywhere else, there are a few rules on what goes here.
 *
 * This class is intended to manage what components are being displayed. It has
 * no knowledge of the underlying data whatsoever, just what components are
 * what. This means that it's hooked to a whole bunch of signals, and changes
 * what's displayed based on those signals. Don't put data dependent components
 * in here.
 */

/* just pass in the home panel's crumb for navigation and an object of objects
 * that viewmanager is supposed to manage
 */
function ViewManager(crumb, objects)
{

    var homepanel = new Ext.Panel({
        title: "Home", 
        fitToFrame: true, 
        autocreate: true, 
        contentEl: 'home', 
        header: false
    });

    if (crumb)
        crumb.panel = homepanel;

    var bcpanel = new Ext.Panel({
        title: "Breadcrumb",
        height: 100,
        autocreate: true,
        anchor: '100%',
        header: false,
        contentEl: 'bccontent'
    });

    var gridstack = new Ext.Panel({
        title: "Grids",
        fitToFrame: true,
        layout: 'card',
        autocreate: true,
        anchor: '100% 100%',
        header: false
    });
    this.gridstack = gridstack;

    var browserpanel = new Ext.Panel({
        title: "Browser",
        fitToFrame: true,
        autocreate: true,
        layout: 'anchor',
        header: false,
        items: [bcpanel, gridstack]
    });

    bigshow = new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            height: 58,
            titlebar: false,
            contentEl: 'header'
        }, 
        objects.queue.panel,
        {
            region: 'center',
            id: 'centerpanel',
            layout: 'card',
            activeItem: 0,
            items: [homepanel, browserpanel]
        }]
    });

    this.init_top_menu = init_top_menu;
    function init_top_menu()
    {
        topmenu = new Ext.Toolbar({renderTo: 'menu', cls:'topmenu', height:18});
        this.srchfld = new Ext.form.TextField({
            emptyText: "Search..."
        });
        var leftspc = new Ext.Toolbar.Fill();
        var homebtn = new Ext.Toolbar.Button({text:'home', cls:'menuitem'});
        var artistbtn= new Ext.Toolbar.Button({text:'artists', cls:'menuitem'});
        var albumbtn= new Ext.Toolbar.Button({text:'albums', cls:'menuitem'});
        var songsbtn= new Ext.Toolbar.Button({text:'songs', cls:'menuitem'});
        var friendsbtn= new Ext.Toolbar.Button({text:'friends', cls:'menuitem'});
        var playlistsbtn= new Ext.Toolbar.Button({text:'playlists', cls:'menuitem'});
        var settingsbtn= new Ext.Toolbar.Button({text:'settings', cls:'menuitem'});
        homebtn.on('click', bread_crumb.go_home, bread_crumb);
        artistbtn.on('click', function() {bread_crumb.go('artist')});
        albumbtn.on('click', function() {bread_crumb.go('album')});
        songsbtn.on('click', function() {bread_crumb.go('song')});
        friendsbtn.on('click', function() {bread_crumb.go('friend')});
        playlistsbtn.on('click', function() {bread_crumb.go('playlist')});
        settingsbtn.on('click', settingspanel.ShowSettings, settingspanel);


        topmenu.add(
            this.srchfld,
            leftspc,
            homebtn,
            artistbtn,
            albumbtn,
            songsbtn,
            friendsbtn,
            playlistsbtn,
            settingsbtn
        );
    }

    this.init_top_menu();

    this.set_panel= set_panel;
    function set_panel(crumb, params, e)
    {
        if (crumb.panel) {
            if (crumb.panel == homepanel) {
                bigshow.getComponent('centerpanel').
                    getLayout().setActiveItem(crumb.panel.id);
                return;
            }
            else if (!gridstack.findById(crumb.panel.id)){
                gridstack.add(crumb.panel);
            }
            gridstack.getLayout().setActiveItem(crumb.panel.id);
            bigshow.getComponent('centerpanel').
                getLayout().setActiveItem(browserpanel.id);
        }
    }

    this.init_search = init_search;
    function init_search(crumb, params, e)
    {
        if (crumb.panel) {
            this.srchfld.validator = 
                function(text) { crumb.panel.search.call(crumb.panel, text)};
        }
    }

    this.add_card = add_card;
    function add_card(newpanel, crumb)
    {
        bigshow.getComponent('centerpanel').add(newpanel);
        if (crumb)
            crumb.panel = newpanel;
    }


}
