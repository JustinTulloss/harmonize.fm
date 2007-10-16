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
    ${h.javascript_include_tag('yui/build/datasource/datasource-beta-min.js')}
    ${h.javascript_include_tag('yui/build/dragdrop/dragdrop-min.js')}
    ${h.javascript_include_tag('yui/build/datatable/datatable-beta-min.js')}
    ${h.javascript_include_tag('yui/build/slider/slider-min.js')}
    ${h.javascript_include_tag('player_init.js')}
</%def>

<div id="top">
    <div id="controls">
        <!-- Put the flash player stuff in here!! -->
        <div id="player"></div>
        <img class="control" src = "/images/back_up.png" onclick="sendEvent('prev')"/>
        <img class="control" src = "/images/play_up.png" onclick="sendEvent('playpause')"/>
        <img class="control" src = "/images/next_up.png" onclick="sendEvent('next')"/>
    </div>
    <div id="status">
        <div id="time">&nbsp;</div>
        <div id="time2">&nbsp;</div>
		<div id="timeline" tabindex="-1"><div id="shuttle"><img src= "/images/shuttle.png"></div></div>
    </div>
</div>
<div id="queue">
    <div class="instruction">
        Drag here to add songs
        <br>-OR-<br>
        Hit the <img class="middle" src="/images/enqueue.png" /> button
    </div>
    ${h.drop_receiving_element("queue", url="enqueue", update="queue")}
</div>
<div id="browser" class="yui-skin-sam">
    &nbsp;Loading...
</div>
