<%inherit file="base.mako" />

<%def name="head_tags()">
    ${h.stylesheet_link_tag('ext-all')}
    ${h.stylesheet_link_tag('ext-ux-slidezone')}
    <title>Rubicon Web Player</title>
    <style type="text/css">
    <%include file="player_css.mako" /> 
    </style>

    ${h.javascript_include_tag('lib/ext-2.0/adapter/ext/ext-base.js')}
    ${h.javascript_include_tag('lib/ext-2.0/ext-all-debug.js')}
    ${h.javascript_include_tag('lib/ext-2.0/source/widgets/ux/SlideZone.js')}
    ${h.javascript_include_tag('lib/ext-2.0/source/widgets/ux/RowExpander.js')}
    ${h.javascript_include_tag('lib/soundmanager2.js')}
    ${h.javascript_include_tag('lib/helpers.js')}
    ${h.javascript_include_tag('player/errmgr.js')}
    ${h.javascript_include_tag('player/viewmgr.js')}
    ${h.javascript_include_tag('player/extbrowser.js')}
    ${h.javascript_include_tag('player/bcmgr.js')}
    ${h.javascript_include_tag('player/settingspanel.js')}
    ${h.javascript_include_tag('player/playqueue.js')}
    ${h.javascript_include_tag('player/player.js')}
    ${h.javascript_include_tag('player/auth.js')}
    ${h.javascript_include_tag('player/metatypeinfo.js')}
    ${h.javascript_include_tag('player/init.js')}

</%def>

<div id="header">
    <div id="menu">
    </div>
    <div id="top">
        <div id="breadcrumb"></div>
        <div id="controls">
            <div id="flash"></div>
            <img class="control mo" id="prevbutton" src = "/images/back.png" />
            <img class="control mo" id="playbutton" src = "/images/play.png" />
            <img class="control mo" id="nextbutton" src = "/images/next.png" />
        </div>
        <div id="status">
            <div id="time">0:00</div>
            <div id="time2">-0:00</div>
            <div id="timeline" tabindex="-1"></div>
        </div>
    </div>
</div>

<div id="home">
    <div id="mainlogo"><img src="/images/homelogo.png" /></div>
</div>
