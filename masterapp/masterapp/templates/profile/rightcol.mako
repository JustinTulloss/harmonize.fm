<%def name="render()">
	<div id="profile-right">
		<div class="profile-pic"><center><img src="${c.user.bigpicture}" /></center></div>
		<div class="home-group">
			<div class="profile-subtitle h-title">Musical Tastes</div>
			<div class="profile-right-content">${c.user.musictastes}</div>
		</div>
		<div class="home-group">
			<div class="profile-subtitle h-title">Top Artists</div>
			${build_top_artists()}
		</div>
	</div>
</%def>


<%def name="build_top_artists()" >
    % for i in xrange(0,10):
        % if len(c.user.top_10_artists)>i:
            <div class="profile-ta">
                <span class="profile-ta-num">${i+1}.</span>
                <span> ${c.user.top_10_artists[i].name}</span>
            </div>
        % endif
    % endfor
</%def>
