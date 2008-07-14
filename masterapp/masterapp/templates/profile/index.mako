##vim:filetype=html:expandtab:tabstop=4
<%namespace name="rightcol" file="rightcol.mako" />
<%namespace name="spotcomment" file="spotcomment.mako" />
<%namespace file="../helpers.mako" import="dl_harmonizer_a"/>

${rightcol.render()}
<div id="profile-body">
	<% own_profile = c.current_user.id == c.user.id %>
    <div class="profile-status">
        <span class="profile-name">${c.user.name}</span>
        % if c.user.nowplaying:
            <span class="profile-nowplaying">
                is listening to ${c.user.nowplaying.title}, by
                ${c.user.nowplaying.artist.name}
            </span>
        % endif
    </div>
    <div class="profile-links">
        <!--
        <div><a href="#/people/recommend">recommend a song to ${c.user.firstname}</a></div>
        -->
		% if own_profile or c.current_user.premium:
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
		% endif
        <div><a target="_blank" href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a></div>
        </a>
    </div>
	<div class="profile-subtitle h-subtitle">Spotlight</div>
	<% spotlights = c.user.get_active_spotlights() %>
	% if spotlights.count() == 0:
		<div>
		<iframe name="dummy_iframe" style="display:none;"></iframe>
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
	% endif
	% for spotlight in c.user.get_active_spotlights():
		${build_spotlight(spotlight, own_profile)}
	% endfor
</div>

<%def name="build_spotlight(spotlight, own_profile)" >
    <div class="profile-sp">
        % if spotlight.albumid and spotlight.album.smallart:
            <div class="profile-sp-albumart">
               ${build_amazon_link(spotlight, h.p_image_tag(spotlight.album.smallart))}
            </div>
        % endif
        <div class="h-title">
            <% 
                enqueue_type = "playlist"
                enqueue_id = "0"
                if spotlight.albumid:
                    enqueue_type = 'album'
                    enqueue_id = spotlight.albumid
                    edit_class = 'edit-spotlight'
                else:
                    enqueue_type = 'playlist'
                    enqueue_id = spotlight.playlistid
                    edit_class = 'edit-playlist-spotlight'
                endif
            %>
				<img src="/images/enqueue.png" onclick="enqueue_spotlight(${enqueue_id}, ${spotlight.uid}, '${enqueue_type}')" />
            % if spotlight.albumid == None:
                Playlist: 
            % endif
            <a class="h-title-a" href="#/browse/friend=${spotlight.uid}/profile=${spotlight.uid}/${enqueue_type}=${enqueue_id}/song">
                ${spotlight.title}
            </a>
            % if not own_profile and spotlight.albumid:
                ${build_amazon_link(spotlight,"(buy)")}
            % endif
 
        </div>
        <div class="profile-sp-artist">
            by ${spotlight.author}
            <span class="spotlight_timestamp">(${spotlight.timestamp.strftime("%b %d")})</span>
            % if own_profile:
                <span class="spot-controls">
                    <a id="${spotlight.id}" class="${edit_class}" href="${c.current_url}">edit</a>
                    <a href="#" onclick="delete_spotlight(${spotlight.id},'${enqueue_type}'); return false;">delete</a>
                </span>
            % endif
        </div>
        <div class="profile-sp-review">${spotlight.comment}</div>

        <%
            edit_spotlight_url = c.current_url + '/spedit/' + str(spotlight.id)
        %>
        
        <div id="spot-edit-${spotlight.id}" class="profile-sp-editcontainer">
            
        </div>
        
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

<%def name="build_amazon_link(spotlight,content)" >
    <%
        asin = c.l_get_asin(spotlight.album.id,'album')
    %>
    <a href="http://www.amazon.com/gp/product/${asin}?ie=UTF8&tag=harmonizefm-20&linkCode=as2&camp=1789&creative=9325&creativeASIN=${asin}" target="_blank">${content}</a><img src="http://www.assoc-amazon.com/e/ir?t=harmonizefm-20&l=as2&o=1&a=B000002ML7" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
</%def>

