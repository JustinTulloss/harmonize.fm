<%inherit file="base.mako" />

<%!
    # Importing simplejson at the module level
    import simplejson
%>

<%def name="head_tags()">
    <title>harmonize.fm | connect with your music</title>

    <script type="text/javascript">
        var global_config = {
            fullname: '${c.fullname}',
            fields: ${simplejson.dumps(c.fields)}
        };
    </script>

    ${parent.head_tags()}
</%def>

<div id="header">
	<div id="song-info-and-controls">
		<div id="now-playing-title">&nbsp;</div>
		<div id="now-playing-artist">&nbsp;</div>
		<div id="now-playing-bar">
			<div id="now-playing-progress"></div>
			<div id="now-playing-time"></div>
		</div>
		<div id="playcontrols">
			<a href="#"><div id="playbutton">
					<div id="play-img" class="play"></div>
			</div></a>
			<a href="#"><div id="prevbutton">
				<div id="prev-img"></div>
			</div></a>
			<a href="#"><div id="nextbutton">
				<div id="next-img"></div>
			</div></a>
			<div id="no-volume"></div>
			<div id="volume"></div>
			<div id="full-volume"></div>
		</div>
	</div>
    <div id="menu"></div>
    <div id="logo">
    	<a href="/"><img src="/images/whiteharmonizefm.png" /></a>
    </div>
</div>

<div id="home">
    <div id="blog">
        % for entry in c.entries:
            ${format_entry(entry)}
        % endfor
    </div>
    <%
        href = None
        if c.platform == 'windows':
            href = '/uploaders/setup.exe'
        elif c.platform == 'mac':
            href = '/uploaders/Harmonize.dmg'
    %>
    % if href:
    <div id="downloadlink">
        <a href="${href}">Download the uploader</a>
    </div>
    % endif
    <div id="mainlogo"><img src="/images/bigharmonized2.png" /></div>
</div>

<div id="bccontent">
    <div id="breadcrumb"></div>
</div>

<%def name="format_entry(entry)">
    <div class="blogentry">
        <div class="blogtitle"> ${entry.title} </div>
        <span class="blogbyline">by<span class="blogauthor"> ${entry.author} </span></span>
        <div class="blogcontent"> ${entry.entry} </div>
    </div>
</%def>
