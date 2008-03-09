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
    var state = 0; //stopped, paused, or playing (0, 1, 2)
    var volume = 80;
    var totalTime;
    var playingsong;
    var nextsong;
    var slider;
    var shuttle;

    this.addEvents({
        nextsong: true,
        prevsong: true,
    });

    /* Soundmanager configuration */
    soundManager.url='/flash/soundmanager2.swf';
    soundManager.debugMode = false;
    soundManager.useConsole = true;
    soundManager.consoleOnly = true;
    soundManager.defaultOptions.volume = 80;

    soundManager.onerror = function () {
        /* TODO: Tie into actual error handling mechanism */
        alert ('An error occurred loading the soundmanager');
    }


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

        shuttle = slider.getSlider('shuttle');
        shuttle.on('drag',
            function() {
                player.seek(this.value/100)
            });
    }

    /* Event handlers */
    this.seek = seek;
    function seek(percent)
    {
        soundManager.setPosition(playingsong, totalTime*percent);
    }

    function playpause(e)
    {
        soundManager.togglePause(playingsong);
    }

    function nextclicked(e)
    {
        /* initiates the nextsong chain of events. True for play now.*/
        this.fireEvent('nextsong', this.playsong);
    }

    function prevclicked(e)
    {
        this.fireEvent('prevsong', this.playsong);
    }
    /* End event handlers */

    this.init_playcontrols = init_playcontrols;
    function init_playcontrols()
    {
        init_seekbar();
        Ext.get('playbutton').on('click', playpause, this);
        Ext.get('nextbutton').on('click', nextclicked, this);
        Ext.get('prevbutton').on('click', prevclicked, this);
    }   

    this.init_playcontrols();

    this.playgridrow = playgridrow
    function playgridrow(grid, songindex, e)
    {
        this.playsong(grid.store.getAt(songindex));
    }

    this.playsong = playsong;
    function playsong (song)
    {
        Ext.Ajax.request({
            url:'/player/songurl/'+song.get('id'),
            success: loadsongurl,
            failure: badsongurl,
            songid: song.get('id'),
            songlength: song.get('length'),
            playnow: true,
            scope: this
        });
    }

    function loadsongurl(response, options)
    {
        if(playingsong)
            soundManager.destroySound(playingsong);
        playingsong = options.songid;

        var me = this;
        soundManager.createSound({
            id: playingsong,
            url:response.responseText,
            volume: volume,
            whileplaying: updatetime
        });
        soundManager.play(playingsong);
    }

    /*note that "this" is the sound below. Might change that.*/
    function updatetime()
    {
        if (this.bytesLoaded != this.bytesTotal)
            total = this.durationEstimate;
        else
            total = this.duration
        Ext.get('time').update(format_time(this.position));
        Ext.get('time2').update('-'+format_time(total-this.position));
        updateseekbar(this.position/total);
    }

    function updateseekbar(percentage)
    {
        /* This actually needs to be percentage*totallength*/
        //slider.setValue(percentage*100);
        shuttle.setPosition([percentage*100]);
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
Ext.extend(Player, Ext.util.Observable);
