<%!
    from pylons import request
%>
<%def name="dl_harmonizer_a()">
    <%
        if 'Windows' in request.headers['User-Agent']:
            href = '/uploaders/Harmonizer Setup.exe'
        elif 'Macintosh' in request.headers['User-Agent']:
            href = '/uploaders/Harmonizer.dmg'
        else:
            href = '/harmonizer-not-supported'
    %>
    % if href:
        <a href="${href}">${caller.body()}</a>
    % endif
</%def>
