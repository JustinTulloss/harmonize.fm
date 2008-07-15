<%namespace name="feed" file="feed.mako" />
<%namespace file="helpers.mako" import="dl_harmonizer_a"/>

<%def name="render(entries)">
		<!--iframe used as target for download uploader link-->
		<iframe name="dummy_iframe" style="display:none;"></iframe>

		<table id="home"><tr><td>
            % if c.num_songs == 0 and c.platform != None:
			<div class="h-title">welcome to harmonize.fm!</div>
            <div id="no-music" class="light-links">
				<div id="no-music-top">
					<img src="/images/oddrow-corners/tr.png" style="float:right;"/>
					<img src="/images/oddrow-corners/tl.png" /> 
				</div>
				<div class="content">
				<h2>Getting started is easy:</h2>
				<ul>
				<li>Click <img src="/images/enqueue.png" /> to listen to your
                friend's Spotlight right away</li>
				<li>Download the <%call expr="dl_harmonizer_a('dummy_iframe')">harmonizer</%call> to share and listen to your own music anywhere</li>
				</ul>
				</div>
				<div id="no-music-bottom">
				<img src="/images/oddrow-corners/br.png" style="float:right;"/>
				<img src="/images/oddrow-corners/bl.png" /> 
				</div>
            </div>					
            % endif

			${feed.render(entries)}

		</td><td id="home-sidebar" class="light-links">
			<div class="home-group">
				<div class="h-title">get the harmonizer</div>
				<center>
					<%call expr="dl_harmonizer_a('dummy_iframe')">
						<img src="/images/orangecircle.png" />
					</%call>
				</center>
			</div>

			<div class="home-group">
				<div class="h-title">places</div>
				<div><a href="#/player/blog">&#187; news</a></div>
				<div><a target="_blank" href="http://blog.harmonize.fm">&#187; blog</a></div>
				<div><a target="_blank" href="/faq">&#187; faq</a></div>
				<div><a target="_blank" href="http://www.facebook.com/apps/application.php?id=${c.appid}">
					&#187; facebook app</a>
				</div>
				<div><a target="_blank" href="/">&#187; harmonize.fm</a></div>
			</div>
		</td></tr></table>
</%def>

%	if hasattr(c, 'main') and c.main:
	${render(c.entries)}
%	endif
