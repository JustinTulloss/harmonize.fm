/*
 * The logic to recommend something to a friend
 */

function make_friend_combo() {
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
        shadow: false,
        emptyText: 'Select a Friend...'
    });
    return field;
}

/* Takes a record and displays a box that you can pick a friend */
function friend_recommend(record) {
    var field = make_friend_combo();
    var id = record.get(typeinfo[record.get('type')].qryindex);
    var url = ['recommend', record.get('type'), id].join('/');
    var button_t = new Ext.Template('<span><button>{0}</button></span>');
    var button = new Ext.Button({
        text: 'recommend',
        template: button_t
    });
    var cancel = new Ext.Button({
        text:'cancel',
        template: button_t
    });
    var entity = record.get(typeinfo[record.get('type')].lblindex);
    var win = new Ext.Panel({
        layout: 'fit',
        resizable: false,
        items: [field],
        buttons: [cancel, button],
        title: '<h1>Recommend to a friend</h1><h2>' + entity + '</h2>',
		baseCls:'x-plain'
    });
    button.setHandler(
        function() {
            show_status_msg("Recommmending...");
            Ext.Ajax.request({
                url: [url, field.getValue()].join('/'),
                success: function(options, response) {
                    show_status_msg("Recommendation Sent");
                }
            });
            hide_dialog();
        }
    );
    cancel.setHandler(function() { hide_dialog(); });
    show_dialog(win, true);
}
