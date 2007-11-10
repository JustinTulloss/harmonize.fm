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
    //this.so.addVariable('file','music/a12883770c0e5760744b24110af1b45ef7083f7b');
    this.so.addVariable('showdigits','false');
    this.so.addVariable('shuffle','false');
    this.so.addVariable('smoothing','false');
    this.so.addVariable('enablejs','true');
    this.so.addVariable('javascriptid','rubiconfl');
    this.so.addVariable('type','mp3');
    this.so.addVariable('usecaptions','false');
    this.so.addVariable('usefullscreen','false');
    this.so.write(div);
    
    //Public functions
    this.sendEvent = sendEvent;
    this.getUpdate = getUpdate;
    this.loadFile = loadFile;
    this.addItem = addItem;
    this.removeItem = removeItem;
    this.seek = seek;

    // these functions are caught by the JavascriptView object of the player.
    function sendEvent(typ,prm) 
    {
        var dm = Ext.getDom('rubiconfl');
        dm.sendEvent(typ,prm);
    }

    //TODO: Make this function less ugly than sin, use a real event model
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
    }

    function leadingZero(nr) {
        if (nr < 10)
            nr = "0" + nr;
        return nr;
    }

    // These functions are caught by the feeder object of the player.
    function loadFile(obj) 
    { 
        Ext.getDom('rubiconfl').loadFile(obj); 
    }

    function addItem(obj,idx) 
    { 
        Ext.getDom('rubiconfl').addItem(obj,idx); 
    }

    function removeItem(idx) 
    { 
        Ext.getDom('rubiconfl').removeItem(idx); 
    }

    function seek(percent)
    {
        sendEvent('scrub', totalTime*percent);
    }
}

/* TODO: Figure out why I can't send updates to an object */
function getUpdate(typ,pr1,pr2,pid)
{
    flplayer.getUpdate(typ, pr1, pr2, pid);
}
