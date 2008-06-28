<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Manage Whitelist</title>
</%def>
<%def name="body()">

    ${h.rails.form('add_to_whitelist', method='POST')}
        <div>Facebook id: ${h.rails.text_field('fbid', size=100, maxlength=255)}</div>
        <div>${h.rails.submit(value='Post', name='post')}</div>
    ${h.rails.end_form()}

    ${h.rails.form('remove_from_whitelist', method='GET')}
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
    ${h.rails.submit(
        value='Remove from Whitelist', 
        name='commitwhitelists', 
        confirm='Are you sure?'
    )}
    ${h.rails.end_form()}

</%def>
<%def name="makewhitelistrow(w)">
    <tr>
        <td>${h.rails.check_box(w.id)}</td>
        <td>${w.fbid}</td>
        <td>${w.registered}</td>
    </tr>
</%def>
