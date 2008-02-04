/* A series of helper functions to display/edit the 
 * list of friends whose music you see
 * 1/26/08 ASM/JMT 
 */

function SettingsPanel(){
    var friendsForm;
    var win;
    var checkboxes;
    var friendStore;
    this.checkboxes = checkboxes;
    this.friendStore = friendStore;
    
    this.makeBoxes = makeBoxes;
    function makeBoxes(record){
        this.checkboxes[this.friendStore.indexOf(record)] = new Ext.form.Checkbox({
            boxLabel:record.get('name'),
            name:record.get('uid'),
            checked:record.get('checked')
        });
    };
    
    this.populateForm = populateForm;
    function populateForm(r, options, success){
        this.checkboxes = [r.length];
        this.friendStore.each(this.makeBoxes, this);
        friendsForm = new Ext.form.FormPanel({
            items:this.checkboxes
        });
        win = new Ext.Window({
            width:500,
            height:300,
            closeAction:'hide',
            autoScroll:true,
            items:friendsForm,
            layout:'fit',
            buttons: [{
                text:'Save',
                handler: function(){
                    win.hide();
                }},{
                text:'Close', 
                handler: function(){
                        win.hide();
                    }
            }]
        });
        win.show();
    };
    
    this.showSettings = showSettings;
    function showSettings(){
        this.friendStore = new Ext.data.JsonStore({
            url:'player/get_checked_friends',
            root:'data',
            fields:['name', 'uid', 'checked']
        });
        //TODO:  status updater (ext.msg.wait?)
        this.friendStore.load({
            scope:this,
            callback: this.populateForm,
            add:false
        });
        this.friendStore.on('loadexception', this.blowsUp, this);
   };
    
    this.blowsUp = blowsUp
    function blowsUp(proxy, o, arg, e){
        alert(e.message);
    }
    this.onSuccess = onSuccess;
    function onSuccess(form, action){
        alert('blao');
    };
    this.onFailure = onFailure;
    function onFailure(form, action){
        alert('failure');
    }

};
