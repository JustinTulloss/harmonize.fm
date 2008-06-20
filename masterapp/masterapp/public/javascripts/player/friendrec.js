/*
 * The logic to recommend something to a friend
 */


/* Takes a record and displays a box that you can pick a friend */
friend_recommend(record) {
    friendstore = new Ext.data.JsonStore({
        url: '/metadata',
        params: {type: friend},
        fields: fields.friend,
        autoLoad: true
    });
    field = new Ext.form.ComboBox({
        store: friendstore,
        displayField: 'name',
        typeAhead: true,
        emptyText: 'Select a Friend...',
    });
    form = new Ext.form.FormPanel({
        items: [field]
    });
    win = new Ext.Window({
        items: [field]
    });
}
