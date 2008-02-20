/* Justin Tulloss
 *
 * The javascript class for manipulating the flash mp3 player
 */

/********
 * Flash Player class.
 * Used to communicate to and from the flash player
 *
 * Params: Takes a div that will be replaced by the flash player swf
 */
function Player(domObj)
{
    var div = domObj;
    // this.some player variables to save
    var currentPosition;
    var currentVolume;
    var currentItem;
    var totalTime;
    this.so = new SWFObject('/flash/mediaplayer.swf','rubiconfl','0','0','7');

    this.so.useExpressInstall('/flash/expressinstall.swf')
    this.so.addParam('allowfullscreen','true');
    this.so.addVariable('showdigits','false');
    this.so.addVariable('shuffle','false');
    this.so.addVariable('smoothing','false');
    this.so.addVariable('enablejs','true');
    this.so.addVariable('javascriptid','rubiconfl');
    this.so.addVariable('type','mp3');
    this.so.addVariable('usecaptions','false');
    this.so.addVariable('usefullscreen','false');
    this.so.write(div);

    // these functions are caught by the JavascriptView object of the player.
    this.sendEvent = sendEvent;
    function sendEvent(typ,prm) 
    {
        Ext.getDom('rubiconfl').sendEvent(typ,prm);
    }

    //TODO: Make this function less ugly than sin, use a real event model
    this.getUpdate = getUpdate;
    function getUpdate(typ,pr1,pr2,pid) {
        if(typ == "time") { currentPosition = pr1; }
        else if(typ == "volume") { currentVolume = pr1; }
        var id = document.getElementById(typ);
        var id2 = document.getElementById(typ + '2');
        mins = Math.round(pr1/60);
        secs = Math.round(pr1%60);
        id.innerHTML = leadingZero(mins) + ":" + leadingZero(secs);
        mins = Math.round(pr2/60);
        secs = Math.round(pr2%60);
        pr2 == undefined ? null: id2.innerHTML = "-"+leadingZero(mins)+":"+leadingZero(secs);
        if (typ == "time") {
            totalTime = pr1 + pr2;
            spos = 100*pr1/totalTime;
            Dom.setStyle('shuttle', 'left', String(spos)+"px");
        }
        if (pr2==0) {
            nextsong();
        }
    }

    function leadingZero(nr) {
        if (nr < 10)
            nr = "0" + nr;
        return nr;
    }

    // These functions are caught by the feeder object of the player.
    function loadFile(obj) 
    { 
    }

    this.addItem = addItem;
    function addItem(obj,idx) 
    { 
        Ext.getDom('rubiconfl').addItem(obj,idx); 
    }

    this.removeItem = removeItem;
    function removeItem(idx) 
    { 
        Ext.getDom('rubiconfl').removeItem(idx); 
    }

    this.seek = seek;
    function seek(percent)
    {
        sendEvent('scrub', totalTime*percent);
    }

    this.playsong = playsong;
    function playsong(song)
    {
        Ext.Ajax.request({
            url:'/player/get_song_url/'+song.get('id'),
            success: loadsongurl,
            failure: badsongurl
        });
    }

    function loadsongurl(response, options)
    {
        Ext.getDom('rubiconfl').loadFile({file:response.responseText});
        sendEvent('playpause');
    }

    function badsongurl(response, options)
    {
        //TODO: Work this into real error handling scheme
        if (response.status == 404)
            Ext.Msg.alert("Not Available", 
                "This song is not available at this time. \
                Perhaps somebody else is listening to it. \
                Try again in a few minutes.");
    }
}

/* TODO: Figure out why I can't send updates to an object */
function getUpdate(typ,pr1,pr2,pid)
{
    flplayer.getUpdate(typ, pr1, pr2, pid);
}
