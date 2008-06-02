##vim:filetype=html:expandtab:tabstop=4
<%namespace name="rightcol" file="rightcol.mako" />

<div style="height:100%; overflow:auto">
<table id="profile-table"><tr><td id="profile-main">
<div id="profile-body">
    <div class="profile-header">
        <div class="profile-info">
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
                <div><a href="#/people/recommend">recommend a song to ${c.user.firstname}</a></div>
                <div><a href="#/bc/friend=${c.user.id}/artist">browse ${c.user.firstname}'s music</a></div>
                <div><a href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a></div>
                </a>
            </div>
        </div>
    </div>
    <div class="profile-spotlight">
        <div class="profile-subtitle">Spotlight</div>
        % for spotlight in c.user.spotlights:
            ${build_spotlight(spotlight)}
        % endfor
    </div>
</div>
</td><td id="rightcol">
	${rightcol.render()}
</td></tr></table>
</div>

<%def name="build_spotlight(spotlight)" >
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
		
        <!--
        <div class="profile-sp-comments">
            <a class="profile-links" href="#/profile_comments/${spotlight.id}">view comments</a>
        </div>
        -->
    </div>
</%def>
