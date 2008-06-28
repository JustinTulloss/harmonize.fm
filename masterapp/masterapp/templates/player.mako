<%inherit file="base.mako" />

<%!
    # Importing simplejson at the module level
    import simplejson
    from masterapp.config.include_files import IncludeFiles
%>

<%def name="head_tags()">
    ${parent.head_tags()}
    % if c.include_files != None:
        % for sheet in c.include_files.stylesheets:
            ${h.stylesheet_link_tag(sheet)}
        % endfor

        <style type="text/css">
        % for template in c.include_files.templated_stylesheets:
            <%include file="${template}" />
        % endfor
        </style>

        % for script in c.include_files.javascripts:
            ${h.javascript_include_tag(script)}
        % endfor
    % endif

    <script type="text/javascript">
        var global_config = {
            fullname: '${c.user.firstname}',
            fields: ${simplejson.dumps(c.fields)},
            fburl: '${c.fburl}',
			uid: ${c.user.id}
        };
    </script>
    <script>
	// Soundmanager configuration
        var soundManager = new SoundManager();
        /* Soundmanager configuration */
        soundManager.url='/flash/soundmanager2.swf';
        soundManager.debugMode = false;
        soundManager.useConsole = false;
        soundManager.consoleOnly = true;
        soundManager.onerror = function () {
			// TODO: Tie into actual error handling mechanism 
			alert ('An error occurred loading the soundmanager');
        }
    </script>
</%def>

<div id="header">
    <div id="song-info-and-controls">
        <div id="now-playing-title">&nbsp;</div>
        <div id="now-playing-artist">&nbsp;</div>
        <div id="now-playing-bar">
            <div id="now-playing-loading"></div>            
            <div id="now-playing-progress"></div>
            <div id="now-playing-time"></div>
            <div id="timeline"></div>
        </div>
        <div id="playcontrols">
            <div id="playbutton" class="pcontrol">
                    <div id="play-img" class="play"></div>
            </div>
            <div id="prevbutton" class="pcontrol">
                <div id="prev-img"></div>
            </div>
            <div id="nextbutton" class="pcontrol">
                <div id="next-img"></div>
            </div>
            <div id="no-volume"></div>
            <div id="volume"></div>
            <div id="full-volume"></div>
        </div>
    </div>
	<div id="topmenu">
		<a href="#">home</a>
		<a href="#/people/profile/${c.user.id}">profile</a>
		<a id="music_link" href="#/bc/artist">
            music
		    <span id="music_menu_link">
                <img id="music_menu_img" src="/images/s.gif" />
            </span>
        </a>
		<a href="#" id="friend_radio_link">radio</a>
		<a href="#/bc/friend">friends</a>
		<a href="#" id="feedback-link">feedback</a>
	</div>
	<div id="status-box"><span></span></div>
    <div id="logo">
        <a href="/"><img src="/images/whiteharmonizefm.png" /></a>
    </div>
</div>


<div id="bccontent">
    <div id="breadcrumb"></div>
</div>

