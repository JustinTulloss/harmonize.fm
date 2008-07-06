<%namespace name="feed" file="feed.mako" />
<%namespace file="helpers.mako" import="dl_harmonizer_a"/>

<%def name="render(entries)">
		<!--iframe used as target for download uploader link-->
		<iframe name="dummy_iframe" style="display:none;"></iframe>

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
				<div><a href="#/player/blog">news</a></div>
				<div><a target="_blank" href="http://blog.harmonize.fm">blog</a></div>
				<div><a target="_blank" href="/faq">faq</a></div>
				<div><a target="_blank" href="http://www.facebook.com/apps/application.php?id=${c.appid}">
                    facebook app</a>
                </div>
				<div><a target="_blank" href="/">harmonize.fm</a></div>
                <div class="home-dllink">
                    <%call expr="dl_harmonizer_a('dummy_iframe')">
                        <img src="/images/dlharmonizerfat.png" />
                    </%call>
                </div>
			</div></div>
			${feed.render(entries)}
		</div>
</%def>

%	if hasattr(c, 'main') and c.main:
	${render(c.entries)}
%	endif
