<%inherit file="base.mako" />

<%!
    # Importing simplejson at the module level
    import simplejson
%>

<%def name="head_tags()">
    ${h.stylesheet_link_tag('core')}
    ${h.stylesheet_link_tag('ext-ux-slidezone')}
    ${h.stylesheet_link_tag('layout')}
    ${h.stylesheet_link_tag('borders')}
    ${h.stylesheet_link_tag('resizable')}
    ${h.stylesheet_link_tag('grid')}
    ${h.stylesheet_link_tag('tree')}
    ${h.stylesheet_link_tag('dd')}
    ${h.stylesheet_link_tag('borders')}
    ${h.stylesheet_link_tag('panel')}
    ${h.stylesheet_link_tag('toolbar')}
    ${h.stylesheet_link_tag('menu')}
    ${h.stylesheet_link_tag('button')}
    ${h.stylesheet_link_tag('box')}
    ${h.stylesheet_link_tag('form')}
    ${h.stylesheet_link_tag('slider')}
    <title>Rubicon Web Player</title>

    <style type="text/css">
    <%include file="player_css/player_css.mako" />
    <%include file="player_css/queue_css.mako" />
    <%include file="player_css/album_details.mako" />
    <%include file="player_css/topbar.mako" />
    <%include file="player_css/statusbar.mako" />
    </style>

    <script type="text/javascript">
        var global_config = {
            fullname: '${c.fullname}',
            fields: ${simplejson.dumps(c.fields)}
        };
    </script>

    ${h.javascript_include_tag('lib/ext-2.1/adapter/ext/ext-base.js')}
    ${h.javascript_include_tag('lib/ext-2.1/ext-all-debug.js')}
    ${h.javascript_include_tag('lib/ext-2.1/source/widgets/ux/SlideZone.js')}
    ${h.javascript_include_tag('lib/ext-2.1/source/widgets/ux/RowExpander.js')}
    ${h.javascript_include_tag('lib/soundmanager2.js')}
    ${h.javascript_include_tag('lib/helpers.js')}
    ${h.javascript_include_tag('player/errmgr.js')}
    ${h.javascript_include_tag('player/viewmgr.js')}
    ${h.javascript_include_tag('player/extbrowser.js')}
    ${h.javascript_include_tag('player/bcmgr.js')}
    ${h.javascript_include_tag('player/settingspanel.js')}
    ${h.javascript_include_tag('player/queueui.js')}
    ${h.javascript_include_tag('player/playqueue.js')}
    ${h.javascript_include_tag('player/player.js')}
    ${h.javascript_include_tag('player/auth.js')}
    ${h.javascript_include_tag('player/metatypeinfo.js')}
    ${h.javascript_include_tag('player/columns.js')}
    ${h.javascript_include_tag('player/init.js')}

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
    	<img src="/images/whiterubicon.png" />
    </div>
</div>

<div id="home">
    <div id="mainlogo"><img src="/images/homelogo.png" /></div>
</div>

<div id="bccontent">
    <div id="breadcrumb"></div>
</div>
