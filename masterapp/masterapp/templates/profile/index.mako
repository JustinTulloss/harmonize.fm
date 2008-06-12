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
        <div><a href="#/bc/friend=${c.user.id}/artist">browse ${c.user.firstname}'s music</a></div>
        <div><a target="_blank" href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a></div>
        </a>
    </div>
    <div id="profile-spotlight">
        <div class="profile-subtitle">Spotlight</div>
        % for spotlight in c.user.get_active_spotlights():
            ${build_spotlight(spotlight, False)}
        % endfor
    </div>
</div>

<%def name="build_spotlight(spotlight, own_profile)" >
    <div class="profile-sp">
        % if spotlight.album.smallart:
            <div class="profile-sp-albumart">
                <img src=${spotlight.album.smallart} />
            </div>
        % endif
        <div class="profile-sp-title"><img src="/images/enqueue.png" onclick="enqueue_album(${spotlight.album.id}, ${spotlight.uid})" />
                ${spotlight.album.title}</div>
        <div class="profile-sp-artist">by ${spotlight.album.artist.name}</div>
        <div class="profile-sp-review">${spotlight.comment}</div>

        <%
            edit_spotlight_url = c.current_url + '/spedit/' + str(spotlight.id)
            edit_class = 'class="profile-sp-comment comment-controls"'
        %>
        
        <div id="spot-edit-${spotlight.id}" class="profile-sp-editcontainer">
            
        </div>
        
        <% 
            comment_url = c.current_url + '/spcomments/' + str(spotlight.id)
            num_comments = len(spotlight.friend_comments) 
            aclass = 'class="profile-sp-comment comment-controls"'
        %>
        
        <div id="spot-comment-${spotlight.id}" class="profile-sp-commentcontainer">
        <a ${edit_class} href="${edit_spotlight_url}">Edit this spotlight</a><br />
        
        % if num_comments == 0 and own_profile:
            
        % elif num_comments == 0 and not own_profile:
            <a ${aclass} href="${comment_url}">Add comment</a>
        % else:
            <a ${aclass} href="${comment_url}">View comments (${num_comments})</a>
        % endif
        ${spotcomment.render(spotlight)}
        </div>
    </div>
</%def>
