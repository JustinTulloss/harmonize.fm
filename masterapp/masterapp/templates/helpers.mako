<%!
    from pylons import request
%>
<%def name="dl_harmonizer_a(target=None)">
    <%
		user_agent = ''
		if request.headers.has_key('User-Agent'):
			user_agent = request.headers['User-Agent']

        if 'Windows' in user_agent:
            href = '/uploaders/Harmonizer Setup.exe'
        elif 'Macintosh' in user_agent:
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
