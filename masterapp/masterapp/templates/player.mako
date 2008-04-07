<%inherit file="base.mako" />

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
    <title>Rubicon Web Player</title>
    <style type="text/css">
    <%include file="player_css/player_css.mako" /> 
    <%include file="player_css/queue_css.mako" /> 
    <%include file="player_css/topbar.mako" /> 
    <%include file="player_css/statusbar.mako" /> 
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
