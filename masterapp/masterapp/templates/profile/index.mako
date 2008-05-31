##vim:filetype=html:expandtab:tabstop=4
<div id="profile-right">
    <div class="profile-pic"><img src="${c.user.bigpicture}" /></div>
    <div class="profile-subtitle">Musical Tastes</div>
    <div class="profile-right-content">${c.user.musictastes}</div>
    <div class="profile-subtitle">Top Artists</div>
    <div class="profile-right-content">
        <div class="profile-ta">
            <span class="profile-ta-num">1.</span>
            <span> Radiohead </span>
        </div>
        <div class="profile-ta">
            <span class="profile-ta-num">1.</span>
            <span> Radiohead </span>
        </div>
        <div class="profile-ta">
            <span class="profile-ta-num">1.</span>
            <span> Radiohead </span>
        </div>
        <div class="profile-ta">
            <span class="profile-ta-num">1.</span>
            <span> Radiohead </span>
        </div>
        <div class="profile-ta">
            <span class="profile-ta-num">1.</span>
            <span> Radiohead </span>
        </div>
        <div class="profile-ta">
            <span class="profile-ta-num">1.</span>
            <span> Radiohead </span>
        </div>
    </div>
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
                <div><a href="#">recommend a song to ${c.user.firstname}</a></div>
                <div><a href="#">browse ${c.user.firstname}'s music</a></div>
                <div><a href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a></div>
                </a>
            </div>
        </div>
    </div>
    <div class="profile-spotlight">
        <div class="profile-subtitle">Spotlight</div>
    </div>
</div>
