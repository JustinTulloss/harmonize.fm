<%inherit file="base.mako" />

<%def name="head_tags()">
    <title>Rubicon Web Player</title>
    <style type="text/css">
    <%include file="player_css.mako" /> 
    <%include file="datatable_css.mako" />
    </style>

    ${h.stylesheet_link_tag('datatable-skin')}
    ${h.javascript_include_tag('swfobject.js')}
    ${h.javascript_include_tag('yui/build/yahoo-dom-event/yahoo-dom-event.js')}
    ${h.javascript_include_tag('yui/build/element/element-beta-min.js')}
    ${h.javascript_include_tag('yui/build/connection/connection-min.js')}
    ${h.javascript_include_tag('yui/build/datasource/datasource-beta-min.js')}
    ${h.javascript_include_tag('yui/build/dragdrop/dragdrop-min.js')}
    ${h.javascript_include_tag('yui/build/datatable/datatable-beta-debug.js')}
    ${h.javascript_include_tag('yui/build/slider/slider-min.js')}
    ${h.javascript_include_tag('browser.js')}
    ${h.javascript_include_tag('bcmgr.js')}
    ${h.javascript_include_tag('playqueue.js')}
    ${h.javascript_include_tag('player.js')}
    ${h.javascript_include_tag('player_init.js')}
</%def>

<div id="menu">
    <div id="searchbar" tabindex="-1">Search...</div>
    <div class="menuitem">${h.link_to_function("Home", "go('home')", Class='menuitem')}</div>
    <div class="menuitem">${h.link_to_function("Artists", "go('home')", Class='menuitem')}</div>
    <div class="menuitem">${h.link_to_function("Albums", "go('home')", Class='menuitem')}</div>
    <div class="menuitem">${h.link_to_function("Songs", "go('home')", Class='menuitem')}</div>
    <div class="menuitem">${h.link_to_function("Friends", "go('home')", Class='menuitem')}</div>
    <div class="menuitem">${h.link_to_function("Genres", "go('home')", Class='menuitem')}</div>
    <div class="menuitem">${h.link_to_function("Settings", "go('home')", Class='menuitem')}</div>
</div>
<div id="top">
    <div id="breadcrumb">Bread Crumb</div>
    <div id="controls">
        <!-- Put the flash player stuff in here!! -->
        <div id="player">Flash Player</div>
        <img class="control" src = "/images/back.png" onclick="flplayer.sendEvent('prev')"/>
        <img class="control" id="playbutton" src = "/images/play.png" onclick="flplayer.sendEvent('playpause')"/>
        <img class="control" src = "/images/next.png" onclick="flplayer.sendEvent('next')"/>
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
<div id="queue">
    <div class="instruction">
        Drag here to add songs
        <br>-OR-<br>
        Hit the <img class="middle" src="/images/enqueue.png" /> button
    </div>
</div>
<div id="browser" class="yui-skin-sam">
    &nbsp;Loading...
</div>