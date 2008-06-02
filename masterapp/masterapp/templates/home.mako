<%namespace name="feed" file="feed.mako" />

<%def name="render(entries)">
	<div id="home">
		<div id="home-bg">
		<div id="home-sidebar">
		<div id="home-sidebar-header">Links</div>
		<%
			href = None
			if c.platform == 'windows':
				href = '/uploaders/setup.exe'
			elif c.platform == 'mac':
				href = '/uploaders/Harmonize.dmg'
		%>
	%	if href:
			<div><a href="${href}">Download the uploader</a></div>
	% 	endif
			<div><a href="#/player/blog">News</a></div>
		</div></div>
		${feed.render(entries)}
		<div id="mainlogo"><img src="/images/bigharmonized2.png" /></div>
	</div>
</%def>

%	if hasattr(c, 'main') and c.main:
	${render(c.entries)}
%	endif
