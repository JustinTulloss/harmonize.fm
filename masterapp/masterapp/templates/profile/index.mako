##vim:filetype=html:expandtab:tabstop=4
<style type="text/css">
    <%include file="/profile/profile.css.mako"/>
</style>

<div class="profile">
    <div id="profile-right">
        <div class="profile-right2">
            <div class="profile-pic"><img src="${c.user.bigpicture}" /></div>
            <div class="profile-right-title">Listening To</div>
            <div class="profile-right-title">Musical Tastes</div>
            <div class="profile-right-content">${c.user.musictastes}</div>
        </div>
    </div>
    <div id="profile-body">
        <div class="profile-header">
            <div class="profile-info">
                <div class="profile-name">${c.user.name}</div>
                <div class="profile-fblink">
                    <a href="http://www.facebook.com/profile.php?id=${c.user.fbid}">view facebook profile</a>
                </div>
            </div>
        </div>
        <div class="profile-spotlight">
            <div class="profile-spotlight-title">&nbsp;Spotlight</div>
        </div>
    </div>
</div>
