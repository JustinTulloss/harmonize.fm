##vim:filetype=html:expandtab:tabstop=4
<div id="profile-right">
    <div class="profile-pic"><img src="${c.user.bigpicture}" /></div>
    <div class="profile-subtitle">Musical Tastes</div>
    <div class="profile-right-content">${c.user.musictastes}</div>
    <div class="profile-subtitle">Top Artists</div>
</div>

<div id="profile-body">
    <div class="profile-header">
        <div class="profile-info">
            <div class="profile-status">
                <span class="profile-name">${c.user.name}</span>
                % if c.user.listeningto:
                    <span class="profile-listeningto">
                        is listening to ${c.user.listeningto}
                    </span>
                % endif
            </div>
            <div class="profile-links">
                <a class="profile-link" href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a>
                <a class="profile-link" href="#">browse ${c.user.firstname}'s music</a>
                <a class="profile-link" href="#">recommend a song to ${c.user.firstname}</a>
                </a>
            </div>
        </div>
    </div>
    <div class="profile-spotlight">
        <div class="profile-subtitle">Spotlight</div>
    </div>
</div>
