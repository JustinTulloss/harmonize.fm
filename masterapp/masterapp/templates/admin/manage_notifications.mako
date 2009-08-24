<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Manage Notifications</title>
</%def>
<%def name="body()">

    ${h.html.tags.form('send_notifications', method='POST')}
    <h4>People who want to be notified:</h4>
    <table>
        <tr>
            <th>CHK</th>
            <th>Email Address</th>
        </tr>
        % for w in c.notifications:
            ${makenotificationrow(w)}
        % endfor
    </table>
    ${h.html.tags.submit(
        value='Notify these people', 
        name='commitnotifications', 
        confirm='Are you sure?'
    )}
    ${h.html.tags.end_form()}

</%def>
<%def name="makenotificationrow(w)">
    <tr>
        <td>${h.html.tags.checkbox(w.id)}</td>
        <td>${w.email}</td>
    </tr>
</%def>
