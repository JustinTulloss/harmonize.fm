/* Justin Tulloss
 *
 * The javascript class for manipulating the flash mp3 player
 * 
 * 03/05/2008 - Cleaning this up. With the ability to investigate the flash
 *              javascript interaction, I think it should be possible to make
 *              this much cleaner.
 */

/********
 * Used to communicate to and from the flash player, controls
 * the interactions with the actual play controllers too.
 *
 */
function Player()
{
    // this.some player variables to save
    var position;
    var volume;
    var totalTime;
    var playingsong;
    var nextsong;

    init_playcontrols();

    /* Soundmanager configuration */
    soundManager.url='/flash/soundmanager2.swf';
    soundManager.debugMode = true;
    soundManager.useConsole = true;

    this.sm.onerror = function () {
        /* TODO: Tie into actual error handling mechanism */
        alert ('An error occurred loading the soundmanager');

    function init_seekbar()
    {
        slider = new Ext.ux.SlideZone('timeline', {
            type: 'horizontal',
            size:100,
            sliderWidth: 13,
            //sliderHeight: 13,
            maxValue: 100,
            minValue: 0,
            sliderSnap: 1,
            sliders: [{
                value: 0,
                name: 'shuttle'
            }]
        });

        slider.getSlider('shuttle').on('drag',
            function() {
                player.seek(this.value/100)
            });
    }

    function init_playcontrols()
    {
        init_seekbar();
    }   

    // these functions are caught by the JavascriptView object of the player.
    this.sendEvent = sendEvent;
    function sendEvent(typ,prm) 
    {
        //Ext.getDom('rubiconfl').sendEvent(typ,prm);
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
        //Ext.getDom('rubiconfl').addItem(obj,idx); 
    }

    this.removeItem = removeItem;
    function removeItem(idx) 
    { 
        //Ext.getDom('rubiconfl').removeItem(idx); 
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
            url:'/player/songurl/'+song.get('id'),
            success: loadsongurl,
            failure: badsongurl
        });
    }

    function loadsongurl(response, options)
    {
        soundManager.play('playingsong', 'response.responseText');
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
    //flplayer.getUpdate(typ, pr1, pr2, pid);
}
