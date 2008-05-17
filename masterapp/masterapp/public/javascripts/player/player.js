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
    var playingsong;
    var nextsong;
    var slider;
    var shuttle;
    var progressbar;

    this.addEvents({
        nextsong: true,
        prevsong: true,
        showprev: true
    });

    /* Soundmanager configuration */
    soundManager.url='/flash/soundmanager2.swf';
    soundManager.debugMode = false;
    soundManager.useConsole = false;
    soundManager.consoleOnly = true;

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
        sound = soundManager.getSoundById(playingsong);
        time = soundduration(sound);
        soundManager.setPosition(playingsong, time*percent);
    }

    function playpause(e)
    {
        if (playingsong)
            soundManager.togglePause(playingsong);
        else
            this.fireEvent('nextsong', this.playsong);
    }

    this.nextclicked = nextclicked;
    function nextclicked(e)
    {
        /* initiates the nextsong chain of events. True for play now.*/
        this.fireEvent('nextsong', this.playsong);
    }

    function prevclicked(e)
    {
        if (playingsong)
        {
            sound = soundManager.getSoundById(playingsong);
            if (sound.position > 1000) {
                soundManager.setPosition(playingsong, 0);
                return;
            }
        }
        this.fireEvent('prevsong', this.playsong);
    }

    function showprev(e)
    {
        this.fireEvent('showprev');
    }

    function hideprev(e)
    {
        this.fireEvent('hideprev');
    }

    /* End event handlers */

    this.init_playcontrols = init_playcontrols;
    function init_playcontrols()
    {
        //init_seekbar();
        Ext.get('playbutton').on('click', playpause, this);
        Ext.get('nextbutton').on('click', nextclicked, this);
        Ext.get('prevbutton').on('click', prevclicked, this);
        Ext.get('prevbutton').on('mouseover', showprev, this);
        Ext.get('prevbutton').on('mouseout', hideprev, this);
    }   

    this.init_playcontrols();

    this.playsong = playsong;
    function playsong (song)
    {
        Ext.Ajax.request({
            url:'/player/songurl/'+song.get('Song_id'),
            success: loadsongurl,
            failure: badsongurl,
            songid: song.get('Song_id'),
            songlength: song.get('Song_length'),
            playnow: true,
            scope: this
        });
    }

    this.stop = stop;
    function stop()
    {
        if (playingsong) {
            soundManager.destroySound(playingsong);
            playingsong = null;
        }
    }

    function loadsongurl(response, options)
    {
        if(playingsong)
            soundManager.destroySound(playingsong);
        playingsong = options.songid;

        soundManager.createSound({
            id: playingsong,
            player: this,
            url:response.responseText,
            volume: volume,
            whileplaying: function(){
                updatetime.call(this.options.player, this)
            },
            onfinish: function(){
                this.options.player.nextclicked.call(this.options.player, this);
            }
        });

        /* create progressbar */
        progressbar = new Ext.ProgressBar({
            renderTo: 'timeline'
        });

        /*finally play */
        soundManager.play(playingsong);
    }

    function updatetime(sound)
    {
        var total = soundduration(sound);
        //Ext.get('time').update(format_time(sound.position));
        //Ext.get('time2').update('-'+format_time(total-sound.position));
        updateseekbar(sound.position/total);
    }

    function soundduration(sound)
    {
        var total;
        if (sound.bytesLoaded != sound.bytesTotal)
            total = sound.durationEstimate;
        else
            total = sound.duration
        return total;
    }


    function updateseekbar(percentage)
    {
        progressbar.updateProgress(percentage);
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

    /* Soundmanager default options */
    soundManager.defaultOptions.volume = 80;
}
Ext.extend(Player, Ext.util.Observable);
