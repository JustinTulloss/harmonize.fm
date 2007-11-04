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
    // some player variables to save
    var currentPosition;
    var currentVolume;
    var currentItem;
    var totalTime;
    var so = new SWFObject('/flash/mediaplayer.swf','rubiconfl','0','0','7');

    so.useExpressInstall('/flash/expressinstall.swf')
    so.addParam('allowfullscreen','true');
    so.addVariable('file','music/a12883770c0e5760744b24110af1b45ef7083f7b');
    so.addVariable('showdigits','false');
    so.addVariable('shuffle','false');
    so.addVariable('smoothing','false');
    so.addVariable('enablejs','true');
    so.addVariable('javascriptid','rubiconfl');
    so.addVariable('type','mp3');
    so.addVariable('usecaptions','false');
    so.addVariable('usefullscreen','false');
    so.write(div);
    
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
        pl = thisMovie("rubiconfl");
        pl.sendEvent(typ,prm); 
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
        thisMovie('rubiconfl').loadFile(obj); 
    }

    function addItem(obj,idx) 
    { 
        thisMovie('rubiconfl').addItem(obj,idx); 
    }

    function removeItem(idx) 
    { 
        thisMovie('rubiconfl').removeItem(idx); 
    }

    function seek(percent)
    {
        sendEvent('scrub', totalTime*percent);
    }

    // This is a javascript handler for the player and is always needed.
    function thisMovie(movieName) 
    {
        if(navigator.appName.indexOf("Microsoft") != -1) {
            return window[movieName];
        } else {
            return document[movieName];
        }
    }
}

/* TODO: Figure out why I can't send updates to an object */
function getUpdate(typ,pr1,pr2,pid)
{
    flplayer.getUpdate(typ, pr1, pr2, pid);
}


