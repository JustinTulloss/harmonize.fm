/*
 * The logic to recommend something to a friend
 */


/* Takes a record and displays a box that you can pick a friend */
function friend_recommend(record) {
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
    var id = record.get(typeinfo[record.get('type')].qryindex);
    var url = ['recommend', record.get('type'), id].join('/');
    var button = new Ext.Button({
        text: 'recommend'
    }); 
    var win = new Ext.Window({
        layout: 'fit',
        items: [field],
        buttons: [button]
    });
    button.setHandler(
        function() {
            set_status_msg("Recommmending...");
            Ext.Ajax.request({
                url: [url, field.getValue()].join('/'),
                success: function(options, response) {
                    set_status_msg("Recommendation Sent");
                }
            });
        }
    );
    win.show();
}
