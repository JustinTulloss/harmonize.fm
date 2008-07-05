<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>File Pipeline Status</title>
</%def>

<%def name="body()">
    <h5> Garbage Collection Enabled: ${c.status['gc']} </h5>
    <h2> Heap Details </h2>
    <code>${c.status['heap']}</code>
    <h2> Summary </h2>
    <table>
    <tr><th>Action</th><th>Files Pending</th><th>Size</th></tr>
    % for action, queue, size in c.status['handlers']:
        <tr><td>${action}</td><td>${len(queue)}</td><td>${size}</td></tr>
    % endfor
    </table>

    <h2> Details </h2>
    % for action, queue, size in c.status['handlers']:
        <h3>${action}</h3>
        % for file in queue:
            <div>${file}</div>
        % endfor
    % endfor

</%def>

