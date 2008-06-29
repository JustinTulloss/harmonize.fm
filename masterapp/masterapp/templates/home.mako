<%namespace name="feed" file="feed.mako" />
<%namespace file="helpers.mako" import="dl_harmonizer_a"/>

<%def name="render(entries)">
		<div id="home">
            <div id="no_music">
            <% 
            href = None
            if c.num_songs == 0:
                if c.platform == 'windows':
                    href = '/uploaders/Harmonizer Setup.exe'
                elif c.platform == 'mac':
                    href = '/uploaders/Harmonize.dmg'
                endif
            endif
            %>
            % if href:
                <h2>You haven't added any music yet.  Install the <a href="${href}">uploader</a> to get started.</h2>
            % endif
            </div>					
			<div id="home-bg">	
			<div id="home-sidebar">			
			<div id="home-sidebar-header" class="h-subtitle">Links</div>
				<div><a href="#/player/blog">News</a></div>
                <div>
                    <%call expr="dl_harmonizer_a()">
                        Download the harmonizer
                    </%call>
                </div>
			</div></div>
			${feed.render(entries)}
			<!--div id="mainlogo"><img src="/images/bigharmonized2.png" /></div-->
		</div>
</%def>

%	if hasattr(c, 'main') and c.main:
	${render(c.entries)}
%	endif
