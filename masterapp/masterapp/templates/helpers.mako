<%!
    from pylons import request
%>
<%def name="dl_harmonizer_a(target=None)">
    <%
        if 'Windows' in request.headers['User-Agent']:
            href = '/uploaders/Harmonizer Setup.exe'
        elif 'Macintosh' in request.headers['User-Agent']:
            href = '/uploaders/Harmonizer.dmg'
        else:
            href = '/harmonizer-not-supported'
            target = '_blank'
    %>
	<a href="${href}"
	% if target != None:
		target="${target}"
	% endif
	>${caller.body()}</a>
</%def>
