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
    init_top_menu();

    homepanel = new Ext.Panel({
        title:"Home", 
        fitToFrame:true, 
        closable:true, 
        autocreate:true, 
        contentEl:'home', 
        header: false
    });

    if (crumb)
        crumb.panel = homepanel;

    bigshow = new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            height: 76,
            titlebar: false,
            contentEl: 'header'
        },{
            region: 'west',
            split: true,
            width: '16%',
            titlebar:false,
            collapsible: true,
            items: [objects.queue.tree]
        }, {
            region: 'center',
            id: 'centerpanel',
            layout: 'card',
            activeItem: 0,
            items: [homepanel]
        }]
    });

    function init_top_menu()
    {
        topmenu = new Ext.Toolbar({renderTo: 'menu', cls:'menu', height:18});
        var homebtn = new Ext.Toolbar.Button({text:'Home', cls:'menuitem'});
        var artistbtn= new Ext.Toolbar.Button({text:'Artists', cls:'menuitem'});
        var albumbtn= new Ext.Toolbar.Button({text:'Albums', cls:'menuitem'});
        var songsbtn= new Ext.Toolbar.Button({text:'Songs', cls:'menuitem'});
        var friendsbtn= new Ext.Toolbar.Button({text:'Friends', cls:'menuitem'});
        var playlistsbtn= new Ext.Toolbar.Button({text:'Playlists', cls:'menuitem'});
        var settingsbtn= new Ext.Toolbar.Button({text:'Settings', cls:'menuitem'});
        homebtn.on('click', bread_crumb.go_home, bread_crumb);
        artistbtn.on('click', function() {bread_crumb.go('artist')});
        albumbtn.on('click', function() {bread_crumb.go('album')});
        songsbtn.on('click', function() {bread_crumb.go('song')});
        friendsbtn.on('click', function() {bread_crumb.go('friend')});
        playlistsbtn.on('click', function() {bread_crumb.go('playlist')});
        //settingsbtn.on('click', settingspanel.ShowSettings, settingspanel);


        topmenu.add(
            homebtn,
            artistbtn,
            albumbtn,
            songsbtn,
            friendsbtn,
            playlistsbtn,
            settingsbtn
        );
    }

    this.set_panel= set_panel;
    function set_panel(crumb, params, e)
    {
        if (crumb.panel) {
            if (!bigshow.getComponent('centerpanel').findById(crumb.panel.id)){
                bigshow.getComponent('centerpanel').add(crumb.panel);
            }
            bigshow.getComponent('centerpanel').
                getLayout().setActiveItem(crumb.panel.id);
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
