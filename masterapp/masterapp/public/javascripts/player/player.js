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

function Player() {
	if (this == window) alert('new not called for Player()');
	var my = this;

    // this.some player variables to save
    var position;
    var state = 0; //stopped, paused, or playing (0, 1, 2)
    var volume = global_config.volume ? global_config.volume : 80;
    var playingsong = null;
    var playingsong_src = null;
	var bufferedsong;
	var buffer_onload; //Should be a fn to call when a song finishes 	loading
	var buffer_loaded;
    var slider;
    var shuttle;
    var progressbar;

    this.addEvents({
        nextsong: true,
        prevsong: true,
        showprev: true
    });
    
    var amazon_link = new Ext.Template('<a href="http://www.amazon.com/gp/product/{asin}?ie=UTF8&tag=harmonizefm-20&linkCode=as2&camp=1789&creative=9325&creativeASIN={asin}" target="_blank">Buy!</a><img src="http://www.assoc-amazon.com/e/ir?t=harmonizefm-20&l=as2&o=1&a={asin}" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />');
	
    function init_seekbar() 
    {
        slider = new Ext.ux.SlideZone('timeline', {
            type: 'horizontal',
            size:250,
            sliderWidth: 13,
            sliderHeight: 13,
            maxValue: 250,
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
                player.seek(this.value/250)
            });
    }
    init_seekbar();
    
    /* Event handlers */
    this.seek = seek;
    function seek(percent)
    {
        sound = soundManager.getSoundById(playingsong);
        time = get_duration();
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

    function nextclicked() {
        /* initiates the nextsong chain of events. True for play now.*/
        my.fireEvent('nextsong', my.playsong);
    }

    function prevclicked(e) {
        if (playingsong) {
            sound = soundManager.getSoundById(playingsong);
			//sound isn't always defined when hitting prev rapidly
            if (sound && sound.position > 1000) {
                soundManager.setPosition(playingsong, 0);
                return;
            }
        }
        this.fireEvent('prevsong', this.playsong);
    }

    function showprev(e) {
        my.fireEvent('showprev');
    }

	function hideprev(e) {
        my.fireEvent('hideprev');
    }

    /* End event handlers */

    this.init_playcontrols = init_playcontrols;
    function init_playcontrols()
    {
        //init_seekbar();
        Ext.get('playbutton').on('click', playpause, this);
        Ext.get('nextbutton').on('click', nextclicked);
        Ext.get('prevbutton').on('click', prevclicked, this);
        Ext.get('prevbutton').on('mouseover', showprev);
        Ext.get('prevbutton').on('mouseout', hideprev);
    }   

    this.init_playcontrols();

    my.playsong = function(song)
    {   
		if (playingsong) {
			soundManager.destroySound(playingsong);
			playingsong = null;
		}

		update_now_playing({
			title : song.get('Song_title'),
			artist : song.get('Artist_name'),
			album : song.get('Album_title'),
			length : song.get('Song_length'),
            id: song.get('Song_id'),
            asin: song.get('Album_asin'),
            mp3asin: song.get('Album_mp3_asin'),
            record: song
        })
            
		set_pause(true);
        /*
        // now update the nowplaying field in the database        
        req_params = {
            id: song.get('Song_id')
        };
        if (song.get('source')) // this handles everything but the radio source
            req_params['source'] = song.get('source');
        if (playqueue.is_friend_radio()) //from radio
            req_params['source'] = 3
        Ext.Ajax.request({
            url: '/player/set_now_playing',
            params: req_params,
            success: function() {return;},
            failure: function() {
                show_status_msg('There was a problem setting your current song statistic.');
            }
        });*/

		if (bufferedsong && bufferedsong == song.get('Song_id')) {
			if (!buffer_loaded) {
				clear_buffer();
			}
			else {
				soundManager.play(bufferedsong);
				soundManager.getSoundById(bufferedsong).setVolume(volume);
				playingsong = bufferedsong;
				bufferedsong = null;
				return;
			}
		}
        //set the params for the songurl and set_now_playing (which is done at the same time):
        req_params = {
            pid: song.get('Song_id'),
        };
        if (song.get('source')) // this handles everything but the radio source
            req_params['source'] = song.get('source');
        if (playqueue.is_friend_radio()) //from radio
            req_params['source'] = 3;
 
		playingsong = song.get('Song_id');
        playingsong_src = req_params['source'];
        Ext.Ajax.request({
            url:'/player/songurl/'+song.get('Song_id'),
            params: req_params,
            success: loadsongurl,
            failure: badsongurl,
            songid: song.get('Song_id'),
            songlength: song.get('Song_length')
        });
    }

    function loadsongurl(response, options) {
        //if this is the next song being buffered, return
        if (playingsong != options.songid) 
			return;

		createSound(response.responseText, playingsong);

        soundManager.play(playingsong);
    }

	function clear_buffer() {
		if (bufferedsong && bufferedsong !== playingsong) {
			soundManager.destroySound(bufferedsong);
		}
		bufferedsong = null;
		buffer_onload = null;
		buffer_loaded = false;
	}

	my.buffersong = function(song) {
		var newid = song.get('Song_id');
		if (newid == bufferedsong || newid == playingsong)
			return;

		clear_buffer();
		bufferedsong = newid;

		function loadbufferedurl(response) {
			if (newid != bufferedsong) return; //Another song buffering
			createSound(response.responseText, bufferedsong);
			buffer_loaded = true;
			soundManager.getSoundById(bufferedsong).load({});
		}
		function buffer() {
	        var req_params = {
                pid: playingsong
            };

            if (playingsong_src) // this handles everything but the radio source
                req_params['source'] = playingsong_src;
            if (playqueue.is_friend_radio()) //from radio
                req_params['source'] = 3;
            
    		Ext.Ajax.request({
				url: '/player/songurl/'+newid,
                params: req_params,
				success: loadbufferedurl,
				failure: badsongurl
			});
			buffer_onload = null;
		}	

		if (!playingsong || !soundManager.getSoundById(playingsong) ||
				soundManager.getSoundById(playingsong).readyState != 3) {
			buffer_onload = buffer;
		}
		else {
			buffer();
		}
	}

    my.stop = function stop() {
        if (playingsong) {
            soundManager.destroySound(playingsong);
            playingsong = null;
        }
		set_pause(false);
		update_now_playing({});
		now_playing_bar.style.visibility = 'hidden';
    }

	function createSound(url, id) {
        soundManager.createSound({
            id: id,
            url: url,
            volume: volume,
            onfinish: nextclicked,
			onload: function() {
				if (buffer_onload)
					buffer_onload();
			},
			multishot: false,
						whileloading: function () {
			    if (id == playingsong) {
			        update_loading_bar(this.bytesLoaded, this.bytesTotal);
			    }
			}
        });
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
        shuttle.setPosition(percentage * 250);
    }

    function update_loading_bar(loaded, total) 
    {
        now_playing_loading.style.width = String(loaded/total*100, 10) + '%';
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

	var now_playing_title = document.getElementById('now-playing-title');
	var now_playing_artist = document.getElementById('now-playing-artist');
	/*Takes an object with the fields {title, artist, album, length, asin, mp3asin} */
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
        
        if (song_info.id) {
        }
        if (!own_record(song_info.record)) {
            
            if (song_info.mp3asin != null && song_info.mp3asin != '0' && song_info.mp3asin != '') {
                //apply template
                Ext.get('amazon_link').update(
                    amazon_link.apply({
                        asin: song_info.mp3asin,
                        album: song_info.album,
                        artist: song_info.artist
                    })
                );
            } else {
                if (song_info.asin != null && song_info.asin != '0' && song_info.asin != '') {
                    Ext.get('amazon_link').update(
                        amazon_link.apply({
                            asin: song_info.asin,
                            album: song_info.album,
                            artist: song_info.artist
                        })
                    );
                } else {
                    //no asin present, set to blank
                    Ext.get('amazon_link').update('');
                }
            }
        } else {
            Ext.get('amazon_link').update('');
        }
		if (song_info.length) 
			reset_progress_bar(song_info.length);
		else
			reset_progress_bar(null);
	}

	var now_playing_bar = document.getElementById('now-playing-bar');
	var now_playing_time = document.getElementById('now-playing-time');
	var now_playing_progress = document.getElementById('now-playing-progress');
	var now_playing_loading = document.getElementById('now-playing-loading');
	function reset_progress_bar(new_song_length) {
		now_playing_bar.style.visibility = 'visible';
		reset_duration(new_song_length);
		update_progress_bar(0);
	}

	function update_progress() {
		if (playingsong !== null) {
			var sound = soundManager.getSoundById(playingsong);
			if (sound) {
				update_duration(sound);
				update_progress_bar(sound.position);
			}
		}
    }

	function update_progress_bar(elapsed) {
		duration = get_duration()
		now_playing_time.innerHTML=
				format_time(elapsed) + ' / ' + format_time(duration);
		if (duration > 0) {
			now_playing_progress.style.width = 
					String(elapsed/duration*100, 10) + '%';
		    shuttle.setPosition([(elapsed/duration)*250]);
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

	/*Volume slider*/
	var volume_control = new Ext.Slider({
		renderTo: 'volume',
		width: 54,
		minValue: 0,
		maxValue: 100,
		value: volume
	});

    var lastsaved = 0;
    function save_volume(){
        Ext.Ajax.request({
            url:'player/set_volume/'+volume,
            disableCaching: false
        });
    }

	function onVolumeChange(slider, value) {
		if (Math.floor(value) != volume) {
			volume = Math.floor(value);
			if (playingsong)
				soundManager.getSoundById(playingsong).setVolume(volume);
		}
        var now = new Date().getTime();
        if (lastsaved+2000 < now) {
            save_volume.defer(2000);
            lastsaved = now;
        }
	}

	volume_control.on('change', onVolumeChange);

	window.onbeforeunload = function() {
		if (playingsong)
			return "You will lose your currently playing song.";
	};

	setInterval(update_progress, 300);
}
Ext.extend(Player, Ext.util.Observable);
