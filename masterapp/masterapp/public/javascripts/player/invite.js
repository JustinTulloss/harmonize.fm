/*
 * This is the dialog that shows up when you click 'invite friend'
 * Dave Paola
 */


/* Takes a record and displays a box that you can pick a friend */
function invite_friend(e) {
    e.preventDefault();
    var friendstore = new Ext.data.JsonStore({
        url: '/metadata',
        baseParams: {
            type: 'friend',
            all: 'true'
        },
        fields: ['name', 'uid'],
        autoLoad: true,
        root: 'data'
    });
    var field = new Ext.form.ComboBox({
        store: friendstore,
        displayField: 'name',
        fieldLabel: 'Friend',
        labelAlign: 'right',
        valueField: 'uid',
        typeAhead: true,
        mode: 'local',
        emptyText: 'Select a Friend...'
    });

    var button = new Ext.Button({
        text: 'invite'
    });
    var cancel = new Ext.Button({
        text:'cancel'
    });

    var win = new Ext.Window({
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
            win.close();
        }
    );
    cancel.setHandler(function(){win.close()});
    win.show();
}
