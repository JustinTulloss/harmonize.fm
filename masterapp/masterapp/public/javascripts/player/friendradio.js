/* friendradio.js - Dave Paola 6/10/2008
 * Contains FriendRadio object functionality (and event handlers)
*/

function FriendRadio() {
    if (this == window) alert('new not called for FriendRadio()');
    var my = this;

    /* Toggle() is called when the friend_radio_link is clicked (an event, see init.js)
     */
    my.toggle = function(e){
        e.preventDefault();
        record = Ext.data.Record.create([]);
        record.type = "friend_radio";            
        record.get = (function(key) {return record[key];});
        playqueue.insert([record]);
		playqueue.dequeue();
    }
}
Ext.extend(FriendRadio, Ext.util.Observable);    
