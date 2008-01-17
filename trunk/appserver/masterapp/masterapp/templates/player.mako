<%inherit file="base.mako" />

<%def name="head_tags()">
    <title>Rubicon Web Player</title>
    <style type="text/css">
    <%include file="player_css.mako" /> 
    </style>

    ${h.stylesheet_link_tag('ext-all')}
    ${h.stylesheet_link_tag('ext-ux-slidezone')}
    ${h.javascript_include_tag('yui/build/yahoo-dom-event/yahoo-dom-event.js')}
    ${h.javascript_include_tag('yui/build/animation/animation-min.js')}
    ${h.javascript_include_tag('yui/build/element/element-beta-min.js')}
    ${h.javascript_include_tag('yui/build/connection/connection-min.js')}
    ${h.javascript_include_tag('ext-2.0/adapter/ext/ext-base.js')}
    ${h.javascript_include_tag('ext-2.0/ext-all-debug.js')}
    ${h.javascript_include_tag('ext-2.0/source/widgets/ux/SlideZone.js')}
    ${h.javascript_include_tag('yui/build/datasource/datasource-beta-min.js')}
    ${h.javascript_include_tag('yui/build/dragdrop/dragdrop-min.js')}
    ${h.javascript_include_tag('yui/build/datatable/datatable-beta-debug.js')}
    ${h.javascript_include_tag('yui/build/slider/slider-min.js')}
    ${h.javascript_include_tag('mousemgr.js')}
    ${h.javascript_include_tag('extbrowser.js')}
    ${h.javascript_include_tag('bcmgr.js')}
    ${h.javascript_include_tag('playqueue.js')}
    ${h.javascript_include_tag('swfobject.js')}
    ${h.javascript_include_tag('player.js')}
    ${h.javascript_include_tag('player_init.js')}
</%def>

<div id="header">
    <div id="menu">
        <!--
        <div id="searchbar" tabindex="-1">Search...</div>
        <div class="menuitem">${h.link_to_function("Home", "go('home')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Artists", "go('artist')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Albums", "go('album')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Songs", "go('song')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Friends", "go('friend')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Genres", "go('genre')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Settings", "go('home')", Class='menuitem')}</div>-->
    </div>
    <div id="top">
        <div id="now-playing">&nbsp;</div>
        <div id="breadcrumb">Bread Crumb</div>
        <div id="controls">
            <!-- Put the flash player stuff in here!! !-->
            <div id="player">Flash Player</div>
            <img class="control mo" id="prevbutton" src = "/images/back.png" />
            <img class="control mo" id="playbutton" src = "/images/play.png" onclick="flplayer.sendEvent('playpause')"/>
            <img class="control mo" id="nextbutton" src = "/images/next.png" />
        </div>
        <div id="status">
            <div id="time">&nbsp;</div>
            <div id="time2">&nbsp;</div>
            <div id="timeline" tabindex="-1"></div>
        </div>
    </div>
</div>

<div id="home">
    <div id="mainlogo"><img src="/images/homelogo.png" /></div>
    <div class="mainmenu">${h.link_to_function("Artists", "go('artist')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Albums", "go('album')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Songs", "go('song')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Friends", "go('friend')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Genres", "go('genre')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Settings", "go('setting')", Class="mainmenuitem")}</div>
</div>
