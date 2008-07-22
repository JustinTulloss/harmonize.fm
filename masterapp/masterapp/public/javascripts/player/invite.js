/*
 * This is the dialog that shows up when you click 'invite friend'
 * Dave Paola
 */


/* Takes a record and displays a box that you can pick a friend */
function invite_friends() {
    var grid = make_invite_grid();
    show_dialog(grid, true);
}

function make_invite_grid() {
    var invite_store = new Ext.data.JsonStore({
        url: '/metadata',
        baseParams: {
            type: 'friend',
            all: 'false',
            nonapp: 'true'
        },
        fields: ['name', 'uid'],
        autoLoad: true,
        root: 'data'
    });

    var filter = new Ext.form.TextField({
        cls:'filter_field',
        emptyText:'Search...',
        enableKeyEvents: true
    });
    
    var button_t = new Ext.Template('<span><button>{0}</button></span>');
    var button = new Ext.Button({
        text: 'invite',
        template: button_t
    });
    var cancel = new Ext.Button({
        text:'cancel',
        template: button_t
    });

    var sm = new Ext.grid.CheckboxSelectionModel();
    var grid = new Ext.grid.GridPanel({
        store: invite_store,
        cm: new Ext.grid.ColumnModel([
            sm,
            {id:'name', header:"Name", dataIndex:'name', width: 120, sortable: true, align: 'left', menuDisabled:true, resizable: false}
        ]),
        height: 300,
        width: 400,
        sm: sm,
        buttons: [cancel, button],
        title: 'Invite friends to Harmonize.fm',
        iconCls: 'icon-grid',
        viewConfig: {
            forceFit:true,
            emptyText: 'Loading...',
            deferEmptyText: false
        },
        tbar: filter,
        trackMouseOver: false
    });
    var selections = [];
    sm.on('rowselect', function(sm, index, record) {
        selections.push(record);
    });
    sm.on('rowdeselect', function(sm, index, record) {
        if (1) return;
        var i = selections.indexOf(record);
        selections.splice(i,1);
    });
    filter.on('keyup', function(e) {
        invite_store.filter('name', filter.getValue(), true, false);
        sm.selectRecords(selections);
    });

    button.setHandler(
        function() {
            show_status_msg("Inviting...");
            invitees = grid.getSelectionModel().getSelections();
            data = [];
            for (i = 0; i < invitees.length; i++) {
                data[i] = invitees[i].get('uid');
            }
            data.join(',');
            Ext.Ajax.request({
                url: ["/people/invite/",data],
                success: function(options, response) {
                    show_status_msg("Invitation Sent");
                }
            });
            hide_dialog();
        }
    );
    cancel.setHandler(function(){hide_dialog()});

    return grid;
}

function make_invite_combo() {
    var invite_store = new Ext.data.JsonStore({
        url: '/metadata',
        baseParams: {
            type: 'friend',
            all: 'false',
            nonapp: 'true'
        },
        fields: ['name', 'uid'],
        autoLoad: true,
        root: 'data'
    });
    var field = new Ext.form.ComboBox({
        store: invite_store,
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
