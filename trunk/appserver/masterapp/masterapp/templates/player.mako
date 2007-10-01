<%inherit file="base.mako" />

<%def name="head_tags()">
     <title>Rubicon Web Player</title>
    ${h.stylesheet_link_tag('player')}
</%def>

<%def name="tag_table(columns,tagdata)">
    <table width="100%">
        <tr>
        % for head in columns:
            <th>${head.capitalize()}</th>
        % endfor
        </tr>
        % for row in tagdata:
            <% element_id = "song-%i" % row.id %>
            <tr id='${element_id}'>
            ${h.draggable_element(element_id, revert = True, ghosting=True)}
            % for col in columns:
                <td>${getattr(row, col)}</td>
            % endfor
            </tr>
        % endfor
    </table>
</%def>

<div id="queue">
    <p class="instruction">
        Drag here to add songs
    </p>
    ${h.drop_receiving_element("queue", url="enqueue", update="queue")}
</div>
<div id="breadcrumb">
    Songs
</div>
<div id="gfilters">
    Showing All Songs
</div>

<div id="browser">
    ${tag_table(c.cols, c.data)}
</div>
<div id="controls">
Back, Play, Forward, Info
</div>
