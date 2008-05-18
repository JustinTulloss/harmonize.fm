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
	if (this == window) alert('new not called for Player()');
	var that = this;

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
        if (playingsong) {
            soundManager.togglePause(playingsong);
			sound = soundManager.getSoundById(playingsong);
			set_pause(!sound.paused);
		}
        else {
            this.fireEvent('nextsong', this.playsong);
			set_pause(false);
		}
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
		update_now_playing({
			title : song.data.Song_title,
			artist : song.data.Artist_name,
			album : song.data.Album_title,
			/*Song length is in milliseconds now,
			  should I convert to seconds here or in the fn... */
			length : song.data.Song_length})

		set_pause(true);
    }

    this.stop = stop;
    function stop()
    {
        if (playingsong) {
            soundManager.destroySound(playingsong);
            playingsong = null;
        }
		set_pause(false);
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
				update_duration(this);
                update_progress_bar(this.position);
				//updatetime.call(this.options.player, this)
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

	var now_playing_title = document.getElementById('now-playing-title');
	var now_playing_artist = document.getElementById('now-playing-artist');
	/*Takes an object with the fields {title, artist, album, length} */
	function update_now_playing(song_info) {
		if (song_info.title)
			now_playing_title.innerHTML = song_info.title;
		else
			now_playing_title.innerHTML = '&nbsp;';

		var new_artist = '&nbsp;';
		if (song_info.artist) {
			new_artist = song_info.artist;
			if (song_info.album)
				new_artist += ' - ' + song_info.album;
		}
		else {
			if (song_info.album)
				new_artist = album;
		}
		now_playing_artist.innerHTML = new_artist;

		if (song_info.length) 
			reset_progress_bar(song_info.length);
		else
			reset_progress_bar(null);
	}

	var now_playing_time = document.getElementById('now-playing-time');
	var now_playing_progress = document.getElementById('now-playing-progress');
	function reset_progress_bar(new_song_length) {
		reset_duration(new_song_length);
		update_progress_bar(0);
	}

	function update_progress_bar(elapsed) {
		duration = get_duration()
		now_playing_time.innerHTML=
				format_time(elapsed) + ' / ' + format_time(duration);
		if (duration > 0) {
			now_playing_progress.style.width = 
					String(elapsed/duration*100, 10) + '%';
		}
		else
			now_playing_progress.style.width = 0;
	}

	var song_length;
	/*Should pass in null if length is not in tags*/
	function reset_duration(tagged_length) {
		song_length = tagged_length;
	}

    function update_duration(sound)
    {
        if (sound.bytesLoaded != sound.bytesTotal) {
			if (song_length === null)
				song_length = sound.durationEstimate;
		}
        else
            song_length = sound.duration;
    }

	function get_duration() {
		if (song_length === null)
			return 0;
		else
			return song_length;
	}

	var play_img = document.getElementById('play-img');
	function set_pause(bool) {
		if (bool) 
			play_img.className = 'pause';
		else
			play_img.className = 'play';
	}
}
Ext.extend(Player, Ext.util.Observable);
