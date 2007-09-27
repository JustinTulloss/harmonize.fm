<%inherit file="base.mako" />

<%def name="head_tags()">
     <title>Rubicon Web Player</title>
</%def>

<%def name="tag_table(columns,tagdata)">
    <table>
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

Welcome! This is gonna be a kick ${c.noun} player.

<div id="queue">
    Drag here to add songs
    ${h.drop_receiving_element("queue", url="enqueue")}
</div>
<div id="browser">
    ${tag_table(c.cols, c.data)}
</div>
<div id="controls">
Back, Play, Forward, Info
</div>
