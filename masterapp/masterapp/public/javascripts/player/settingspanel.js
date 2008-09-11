/*  New settingspanel.js making the friends
 *  panel a grid instead of a form
 *  2/18/08 by A-Mo */
 
function SettingsPanel(){
    var win;
    var friendGrid;    
    var friendStore;
    this.win=win;
    this.friendStore = friendStore;

    this.MakeGrid = function(){    
        var sm = new Ext.grid.CheckboxSelectionModel({dataIndex:"checked"});
        this.friendGrid = new Ext.grid.GridPanel({
            store:this.friendStore,
            cm: new Ext.grid.ColumnModel([
                sm,
               {header: "name", dataIndex: "name"}]),
            width:500,
            height:300,
            sm:sm,
            iconCls:'icon-grid',
            frame:true
        });
       
    };
    
    this.PopulateGrid = function PopulateGrid(){
        this.MakeGrid();
        if(!win){
            win = new Ext.Window({
                width:500,
                height:300,
                closeAction:'hide',
                autoScroll:true,
                items:this.friendGrid,
                layout:'fit',
                buttons: [{
                    text:'Save',
                    handler: function(){
                        win.hide();
                       // this.CommitStoreChanges();
                    }},{
                    text:'Close', 
                    handler: function(){
                            win.hide();
                        }
                }]
            });
        }
        win.show();
        //win.on("close", this.friendStore.rejectChanges);
        var checkedRecs = this.friendStore.query("checked", "true", true, false);
        this.friendGrid.getSelectionModel().selectRecords(checkedRecs.items);
    };
    
    this.CommitStoreChanges = function () {};
    
    this.ShowSettings = function(){
        var friend = Ext.data.Record.create([
            {name:"name"},
            {name:"uid"},
            {name:"checked"}
        ]);
        var reader = new Ext.data.JsonReader({
            root:"data",
            id:"uid"
        }, friend);
        
        this.friendStore = new Ext.data.Store({
            url:'player/get_checked_friends',
            reader:reader,
            root:'data',
            fields:['name', 'uid', 'checked']
        });
        //TODO:  status updater (ext.msg.wait?)
        this.friendStore.load({
            scope:this,
            callback:this.PopulateGrid,
            add:false
        });
    };
}
