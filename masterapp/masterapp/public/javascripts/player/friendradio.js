/* friendradio.js - Dave Paola 6/10/2008
 * Contains FriendRadio object functionality (and event handlers)
*/

function FriendRadio() {
    if (this == window) alert('new not called for FriendRadio()');
    var my = this;
       
    this.addEvents({
        nextradiosong:true,
        playsong: true
    });
    
    var enabled = false;
    var enabling = false;
    
    my.toggle = function(){
        if (my.enabled) {
            my.enabled = false;
            Ext.get("friend_radio_status").update(" (OFF)");
        } else {
            my.enabled = true;
            Ext.get("friend_radio_status").update(" (ON)");
            my.nextSong();
        }
    }
    
    my.nextSong = function () {
        //ajax query to retrieve the song id of the next song to play
         Ext.Ajax.request({
            url:'/metadata/next_radio_song',
            success: my.radio_handler,
            failure: my.radio_handler_failure
        });
    }
    
    my.radio_handler = function(response, options) {
        var next_song = eval('(' + response.responseText + ')');
        next_song = next_song.data[0];
        next_song.get = (function(key) {return next_song[key];});
        my.enabling = false;
        my.fireEvent('playsong',next_song);
    }
    
    my.radio_handler_failure = function(response, options) {
        alert("radio_handler_failure");        
        alert(reponse.responseText);
    }
}
Ext.extend(FriendRadio, Ext.util.Observable);    