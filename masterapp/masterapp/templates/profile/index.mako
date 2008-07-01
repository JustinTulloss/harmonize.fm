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
            ${build_spotlight(spotlight, c.current_uid == c.user.id)}
        % endfor
    </div>
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
            ${spotlight.title}
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
<%def name="build_amazon_link(spotlight,content)" >
    <a href="http://www.amazon.com/gp/product/${spotlight.album.asin}?ie=UTF8&tag=harmonizefm-20&linkCode=as2&camp=1789&creative=9325&creativeASIN=${spotlight.album.asin}" target="_blank">${content}</a><img src="http://www.assoc-amazon.com/e/ir?t=harmonizefm-20&l=as2&o=1&a=B000002ML7" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
</%def>

