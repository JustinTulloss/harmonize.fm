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
				<h1>Welcome to harmonize.fm!</h1>
				<h2>Here's how to get started:</h2>
				<ul>
					<li>Add music with the <a href="${href}">harmonizer</a></li>
					<li>Listen to your music with the 
						<span id="music">music <img src="/images/s.gif" class="music_menu_img"/></span> 
						button in the top right</li>
					<li>Share music with your friends by creating a 
						<img src="/images/spotlight.png" />Spotlight 
						or by 
						<img src="/images/recommend.png" />recommending music</li>
				</ul>
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
