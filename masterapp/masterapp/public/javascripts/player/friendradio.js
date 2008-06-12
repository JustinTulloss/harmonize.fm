/* friendradio.js - Dave Paola 6/10/2008
 * Contains FriendRadio object functionality (and event handlers)
*/

function FriendRadio() {
    if (this == window) alert('new not called for FriendRadio()');
    var my = this;
    
    my.toggle = function(){
        record = Ext.data.Record.create([]);
        record.type = "friend_radio";            
        record.get = (function(key) {return record[key];});
        playqueue.insert([record]);
    }
}
Ext.extend(FriendRadio, Ext.util.Observable);    