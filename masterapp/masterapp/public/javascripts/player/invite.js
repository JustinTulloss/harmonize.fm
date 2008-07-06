/*
 * This is the dialog that shows up when you click 'invite friend'
 * Dave Paola
 */


/* Takes a record and displays a box that you can pick a friend */
function invite_friend() {
    var field = make_friend_combo();
    var button_t = new Ext.Template('<span><button>{0}</button></span>');
    var button = new Ext.Button({
        text: 'invite',
        template: button_t
    });
    var cancel = new Ext.Button({
        text:'cancel',
        template: button_t
    });

    var win = new Ext.Panel({
        layout: 'fit',
        resizable: false,
        items: [field],
        buttons: [cancel, button],
        title: 'Invite a friend to Harmonize.fm'
    });
    button.setHandler(
        function() {
            show_status_msg("Inviting...");
            Ext.Ajax.request({
                url: ["/people/invite",field.getValue()].join('/'),
                success: function(options, response) {
                    show_status_msg("Invitation Sent");
                }
            });
            hide_dialog();
        }
    );
    cancel.setHandler(function(){hide_dialog()});
    show_dialog(win, true);
}
