<%inherit file="base.mako" />

<%def name="head_tags()">
    <title>Rubicon Web Player</title>
    <style type="text/css">
    <%include file="player_css.mako" /> 
    <%include file="datatable_css.mako" />
    <%include file="ext-all-css.mako" />
    </style>

    ${h.javascript_include_tag('yui/build/yahoo-dom-event/yahoo-dom-event.js')}
    ${h.javascript_include_tag('yui/build/animation/animation-min.js')}
    ${h.javascript_include_tag('yui/build/element/element-beta-min.js')}
    ${h.javascript_include_tag('yui/build/connection/connection-min.js')}
    ${h.javascript_include_tag('ext/adapter/yui/ext-yui-adapter.js')}
    ${h.javascript_include_tag('ext/ext-all-debug.js')}
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
        <div id="searchbar" tabindex="-1">Search...</div>
        <div class="menuitem">${h.link_to_function("Home", "go('home')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Artists", "go('artist')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Albums", "go('album')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Songs", "go('song')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Friends", "go('friend')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Genres", "go('genre')", Class='menuitem')}</div>
        <div class="menuitem">${h.link_to_function("Settings", "go('home')", Class='menuitem')}</div>
    </div>
    <div id="top">
        <div id="breadcrumb">Bread Crumb</div>
        <div id="controls">
            <!-- Put the flash player stuff in here!! !-->
            <div id="player">Flash Player</div>
            <img class="control mo" id="prevbutton" src = "/images/back.png" onclick="flplayer.sendEvent('prev')"/>
            <img class="control mo" id="playbutton" src = "/images/play.png" onclick="flplayer.sendEvent('playpause')"/>
            <img class="control mo" id="nextbutton" src = "/images/next.png" />
        </div>
        <div id="status">
            <div id="time">&nbsp;</div>
            <div id="time2">&nbsp;</div>
            <div id="timeline" tabindex="-1">
                <div id="shuttle">
                    <img src= "/images/shuttle.png">
                </div>
            </div>
        </div>
    </div>
</div>
<div id= "queue-container">
    <div id="queue-menu">
        <a class="queue-menu-item" id="clear-queue" onclick="playqueue.clearQueue();" href="#">clear</a>
        <a class="queue-menu-item" id="save-queue" onclick="alert('This has not yet been implemented');" href="#">save</a>
    </div>
    <div id= "queue"></div>
<div>
<div id="home">
    <div id="mainlogo"><img src="/images/homelogo.png" /></div>
    <div class="mainmenu">${h.link_to_function("Artists", "go('artist')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Albums", "go('album')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Songs", "go('song')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Friends", "go('friend')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Genres", "go('genre')", Class="mainmenuitem")}</div>
    <div class="mainmenu">${h.link_to_function("Settings", "go('setting')", Class="mainmenuitem")}</div>
</div>
<div id="browser">
    Loading...
</div>
