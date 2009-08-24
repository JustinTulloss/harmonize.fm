<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Manage Whitelist</title>
</%def>
<%def name="body()">

    ${h.html.tags.form('add_to_whitelist', method='POST')}
        <div>Facebook id: ${h.html.tags.text('fbid', size=100, maxlength=255)}</div>
        <div>${h.html.tags.submit(value='Post', name='post')}</div>
    ${h.html.tags.end_form()}

    ${h.html.tags.form('remove_from_whitelist', method='GET')}
    <h4>Whitelisted facebook ids</h4>
    <table>
        <tr>
            <th>RM</th>
            <th>Facebook ID</th>
            <th>Registered</th>
        </tr>
        % for w in c.whitelists:
            ${makewhitelistrow(w)}
        % endfor
    </table>
    ${h.html.tags.submit(
        value='Remove from Whitelist', 
        name='commitwhitelists', 
        confirm='Are you sure?'
    )}
    ${h.html.tags.end_form()}

</%def>
<%def name="makewhitelistrow(w)">
    <tr>
        <td>${h.html.tags.checkbox(w.id)}</td>
        <td>${w.fbid}</td>
        <td>${w.registered}</td>
    </tr>
</%def>
