<%inherit file="base.mako" />

<%def name="head_tags()">
     <title>Rubicon Web Player</title>
    ${h.stylesheet_link_tag('player')}
    ${h.stylesheet_link_tag('datatable-skin')}
    ${h.javascript_include_tag('swfobject.js')}
    ${h.javascript_include_tag('yui/build/yahoo-dom-event/yahoo-dom-event.js')}
    ${h.javascript_include_tag('yui/build/element/element-beta-min.js')}
    ${h.javascript_include_tag('yui/build/datasource/datasource-beta-min.js')}
    ${h.javascript_include_tag('yui/build/dragdrop/dragdrop-min.js')}
    ${h.javascript_include_tag('yui/build/datatable/datatable-beta-min.js')}
    ${h.javascript_include_tag('player_init.js')}
</%def>

<%def name="tag_table(columns,tagdata)">
    <table width="100%">
        <tr>
        % for head in columns:
            <th class="tags">${head.capitalize()}</th>
        % endfor
        </tr>
        % for row in tagdata:
            <% element_id = "%i" % row.id %>
            <tr id='${element_id}' class="datarow">
            ${h.draggable_element(element_id, revert = True, ghosting=True)}
            % for col in columns:
                <td>${getattr(row, col)}</td>
            % endfor
            </tr>
        % endfor
    </table>
</%def>

<div id="top">
    <div id="controls">
        <!-- Put the flash player stuff in here!! -->
        <div id="player">Flash Player</div>
        <img class="control" src = "/images/back_up.png" />
        <img class="control" src = "/images/play_up.png" />
        <img class="control" src = "/images/next_up.png" />
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
    Stuff
</div>
