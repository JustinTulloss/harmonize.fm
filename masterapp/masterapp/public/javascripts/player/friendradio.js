/* friendradio.js - Dave Paola 6/10/2008
 * Contains FriendRadio object functionality (and event handlers)
*/

function FriendRadio() {
    var my = this;

    /* Toggle() is called when the friend_radio_link is clicked (an event, see init.js)
     */
    my.toggle = function(e){
        e.preventDefault();
        record = Ext.data.Record.create([]);
        record.type = "friend_radio";            
        record.get = function(key) { return record[key]; };
		record.set = function(key, val) { record[key] = value; return value; };
        playqueue.insert([record], true);
    };
}
Ext.extend(FriendRadio, Ext.util.Observable);    
