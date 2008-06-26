##vim:filetype=html:expandtab:tabstop=4
<%namespace name="rightcol" file="rightcol.mako" />
<%namespace name="spotcomment" file="spotcomment.mako" />

${rightcol.render()}
<div id="profile-body">
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
        <div id="friend_music_menu_link">
            <a href="#/action/browse_friend/${c.user.id}">
                browse ${c.user.firstname}'s music
            </a>
        </div>
        <div><a target="_blank" href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a></div>
        </a>
    </div>
    <div id="profile-spotlight">
        <div class="profile-subtitle h-subtitle">Spotlight</div>
        % for spotlight in c.user.get_active_spotlights():
            % if spotlight.album != None:            
                ${build_spotlight(spotlight, c.current_uid == c.user.id)}
            % elif spotlight.playlist != None:
                ${build_playlist_spotlight(spotlight, c.current_uid == c.user.id)}
            % endif
        % endfor
    </div>
</div>

<%def name="build_spotlight(spotlight, own_profile)" >
    <div class="profile-sp">
        % if spotlight.album.smallart:
            <div class="profile-sp-albumart">
                ${h.p_image_tag(spotlight.album.smallart)}
            </div>
        % endif
        <div class="h-title">
				<img src="/images/enqueue.png" onclick="enqueue_album(${spotlight.album.id}, ${spotlight.uid})" />
                ${spotlight.album.title}</div>
        <div class="profile-sp-artist">
            by ${spotlight.album.artist.name} <span class="spotlight_timestamp">(${spotlight.timestamp.strftime("%b %d")})</span>
            % if own_profile:
                <span class="spot-controls">
                    <a id="${spotlight.id}" class="edit-spotlight" href="${c.current_url}">edit</a>
                    <a href="#" onclick="delete_spotlight(${spotlight.id},'album'); return false;">delete</a>
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
<%def name="build_playlist_spotlight(spotlight, own_profile)" >
    <div class="profile-sp">
        <div class="h-title">
            <img src="/images/enqueue.png" onclick="enqueue_playlist(${spotlight.playlist.id}, ${spotlight.uid})" />
            ${spotlight.playlist.name}
        </div>
        <div class="profile-sp-artist">
            by ${spotlight.user.name} <span class="spotlight_timestamp">(${spotlight.timestamp.strftime("%b %d")})</span>
            % if own_profile:
                <span class="spot-controls">
                    <a id="${spotlight.id}" class="edit-playlist-spotlight" href="${c.current_url}">edit</a>
                    <a href="#" onclick="delete_spotlight(${spotlight.id},'playlist'); return false;">delete</a>
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
