##vim:filetype=html:smarttab:expandtab:tabstop=4
<%namespace name="rightcol" file="rightcol.mako" />
<%namespace name="spotcomment" file="spotcomment.mako" />
<%namespace file="../helpers.mako" import="dl_harmonizer_a"/>
<%!
from masterapp.lib.html import linebreaks, urlize
%>

${rightcol.render()}
<div id="profile-body">
    <% 
		own_profile = c.current_user.id == c.user.id
	 	old_spotlights_active = own_profile or c.current_user.premium
	%>
    <div class="profile-status home-group">
		<div class="profile-links">
			<div id="friend_music_menu_link">
				<a href="#/action/browse_friend/${c.user.id}">
					browse 
					% if own_profile:
						your
					% else:
						${c.user.firstname}'s 
					% endif
					music
				</a>
			</div>
			<div><a target="_blank" href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a></div>
			</a>
		</div>
        <span class="profile-name">${c.user.name}</span>
        % if c.user.nowplaying:
            <div class="profile-nowplaying">
                is listening to ${c.user.nowplaying.title}, by
                ${c.user.nowplaying.artist.name}
            </div>
        % endif
    </div>
	<div class="home-group">
    <div class="profile-subtitle h-title">spotlights</div>
    <% spotlights = c.user.get_active_spotlights() %>
    % if spotlights.count() == 0:
        <div class="profile-group">
        <iframe name="dummy_iframe" style="display:none;"></iframe>
		<div>
        % if own_profile:
            You haven't added any spotlights yet, 
            % if c.user.song_count == 0:
                download the 
                <%call expr="dl_harmonizer_a('dummy_iframe')">harmonizer</%call>
                to add music.
            % else:
                click the <img class="favicon" src="/images/spotlight.png"/>Spotlight button on an album or playlist to create one.
            % endif
        % else:
            ${c.user.firstname} hasn't created any spotlights yet.
        % endif
		</div>
        </div>
    % endif
    % for spotlight in spotlights:
        ${build_spotlight(spotlight, own_profile)}
    % endfor
	</div>
    % if own_profile:
		<div class="home-group">
			<div class="profile-subtitle h-title">recommendations</div>
			<% recs = c.user.recommendations %>
			% if recs.count() == 0:
				<div class="profile-group">
					<div>You haven't received any recommendations yet.</div>
				</div>
			% else:
				% for rec in recs:
					${build_recommendation(rec)}
				% endfor
			% endif
		</div>
    % endif
	<% old_spotlights = c.user.inactive_spotlights %>
	% if old_spotlights.count() > 0:
		<div class="home-group">
			<div class="h-title">past spotlights</div>
			% for spotlight in old_spotlights:
				${build_spotlight(spotlight, own_profile, old_spotlights_active)}
			% endfor
	% endif

</div>

<%def name="build_spotlight(spotlight, own_profile, active=True)" >
    <div class="profile-group">
        % if spotlight.albumid and spotlight.album.smallart:
            <div class="profile-albumart">
               <%call expr="build_amazon_link(spotlight.album)">
                    ${h.p_image_tag(spotlight.album.smallart)}
               </%call>
            </div>
        % endif
        <h3>
            <% 
                if spotlight.albumid:
                    edit_class = 'edit-spotlight'
                else:
                    edit_class = 'edit-playlist-spotlight'
                endif
            %>
			% if active:
				<a href="#/action/enqueue/${spotlight.type}/${spotlight.typeid}&Friend_id=${spotlight.uid}">
					<img src="/images/enqueue.png" />
				</a>
			% else:
				<img class="fake-enqueue" src="/images/s.gif" />
			% endif
            % if spotlight.albumid == None:
                Playlist: 
            % endif
            <a class="h-title-a" href="#/browse/friend=${spotlight.uid}/profile=${spotlight.uid}/${spotlight.type}=${spotlight.typeid}/song">
                ${spotlight.title}
            </a>
            % if not own_profile and spotlight.albumid:
                <%call expr="build_amazon_link(spotlight.album)">
                    <img src="/images/cart.png" />
                </%call>
            % endif
        </h3>
        <div class="profile-artist">
            by ${spotlight.author}
			% if spotlight.timestamp:
				<span class="spotlight_timestamp">(${spotlight.timestamp.strftime("%b %d")})</span>
			% endif
            % if own_profile:
                <span class="spot-controls">
                    <a id="${spotlight.id}" class="${edit_class}" href="${c.current_url}">edit</a>
                    <a href="#" onclick="delete_spotlight(${spotlight.id},'${spotlight.type}'); return false;">delete</a>
                </span>
            % endif
        </div>
        <div class="profile-review">${linebreaks(urlize(spotlight.comment))}</div>
        
        <% 
            comment_url = c.current_url + '/spcomments/' + str(spotlight.id)
            num_comments = len(spotlight.friend_comments) 
            aclass = 'class="view-comment"'
        %>
        
        <div id="spot-comment-${spotlight.id}" class="profile-sp-commentcontainer">
          
        % if num_comments == 0:
            <a ${aclass} href="${comment_url}">comment</a>
        % else:
            <a ${aclass} href="${comment_url}">comments (${num_comments})</a>
        % endif
            <a class="hide-comment" href="${c.current_url}">hide comments</a>

        ${spotcomment.render(spotlight)}
        </div>
    </div>
</%def>

<%def name="build_amazon_link(album)" >
    <%
        asin = c.l_get_asin(album.id,'album')
    %>
    % if asin != "0":
        <a href="http://www.amazon.com/gp/product/${asin}?ie=UTF8&tag=harmonizefm-20&linkCode=as2&camp=1789&creative=9325&creativeASIN=${asin}" target="_blank">${caller.body()}</a><img src="http://www.assoc-amazon.com/e/ir?t=harmonizefm-20&l=as2&o=1&a=B000002ML7" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
    % endif
</%def>

<%def name="build_title(action)">
    <h3>
    <a href="#/action/enqueue/${action}"><img src="/images/enqueue.png"/></a>
    ${caller.body()}
    </h3>
</%def>

<%def name="build_album_art(album)">
    % if album != None and album.smallart != None:
        <div class="profile-albumart">
            <%call expr="build_amazon_link(album)">
                ${h.p_image_tag(album.smallart)}
            </%call>
        </div>
    % endif 
</%def>

<%def name="build_album_rec(rec)">
    ${build_album_art(rec.album)}

    <%call expr="build_title('album/'+str(rec.albumid)+'&Friend_id='+str(rec.recommenderid))">
        ${rec.album.title}
    </%call>

    ${build_recommend_common(rec, rec.album.artist)}
</%def>

<%def name="build_song_rec(rec)">
    ${build_album_art(rec.song.album)}

    <%call expr="build_title('song/'+str(rec.songid)+'&Friend_id='+str(rec.recommenderid))">
        ${rec.song.title}
    </%call>

    ${build_recommend_common(rec, rec.song.album.artist)}
</%def>

<%def name="build_playlist_rec(rec)">
    <%call expr="build_title('playlist/'+str(rec.playlistid)+'&Friend_id='+str(rec.recommenderid))">
        Playlist: ${rec.playlist.name}
    </%call>

    ${build_recommend_common(rec, rec.playlist.owner)}
</%def>

<%def name="build_recommend_common(rec, artist)">
    <div class="profile-artist">
        by ${artist.name}
    </div>

    % if rec.comment != None:
        <div class="profile-review">${rec.comment}</div>
    % endif

    <div class="profile-recommender">
        recommended by <a href="#/people/profile/${rec.recommenderid}">
            ${rec.recommender.name}
        </a>
    </div>
</%def>

<%def name="build_recommendation(rec)">
    <div class="profile-group">
    % if rec.album != None:
        ${build_album_rec(rec)}
    % elif rec.playlist != None:
        ${build_playlist_rec(rec)}
    % else:
        ${build_song_rec(rec)}
    % endif
    </div>
</%def>
