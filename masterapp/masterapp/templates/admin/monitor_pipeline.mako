<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>File Pipeline Status</title>
</%def>

<%def name="body()">
    <h2> Summary </h2>
    <table>
    <tr><th>Action</th><th>Files Pending</th></tr>
    % for action, queue in c.status:
        <tr><td>${action}</td><td>${len(queue)}</td></tr>
    % endfor
    </table>

    <h2> Details </h2>
    % for action, queue in c.status:
        <h3>${action}</h3>
        % for file in queue:
            <div>${file}</div>
        % endfor
    % endfor

</%def>

