.profile-name {
    font-size: 24pt;
    font-family: "Trebuchet MS", "Lucida Sans Unicode", sans-serif;
}

.profile-nowplaying {
    font-weight: bold;
}

.profile-status {
    color: ${c.profile.dark_txt};
    border-bottom: 1px solid ${c.profile.profile_border};
	padding-left: 25px
}

.profile-links {
    float: right;
}

.profile-links div {
	text-align: right;
	padding-top: 3px;
}

#profile-body a {
    color: ${c.profile.profile_links};
}

#profile-body a:hover {
    color: ${c.profile.click}
}

#profile-body {
    padding: 20px 14px 20px 0;
	overflow: hidden;
}

#profile-body > div {
	margin-left: 25px;
	/*padding-left: 5px;*/
}

#profile-body h3 {
	margin: 0;
	padding:  0;
	font-weight: normal;
	font-size: 14px;
	color: ${c.profile.dark_txt};
}

#profile-body h3 a {
	color: ${c.profile.dark_txt};
	text-decoration: none;
}

#profile-body h3 a:hover {
	color: ${c.profile.click};
}

#profile-right {
    padding: 10px 14px;
    margin-top: 10px;
    margin-bottom: 10px;
    border-left: 1px solid ${c.profile.profile_border};
	width: 200px;
	float: right;
	background-color: white;
}

#profile-body .profile-group {
	padding-left: 2px;
    clear: right;
    padding-top: 5px;
	/*margin-left: 5px;*/
}

.profile-group > div {
    margin-left: 25px;
}

.profile-group > .home-group {
	margin-left: 0;
}

.profile-group > .h-title {
    margin-left: 0;
}

div.profile-albumart {
    float: right;
}

.profile-artist {
    color: ${c.profile.profile_links};
}

.profile-sp-artist a {
    text-align: right;
}

.profile-review {
    padding-left: 8px;
    margin-bottom: 4px;
}

.profile-sp-comment {
    clear: right;
	margin-top: 5px;
}

.comments-body {
	margin-top: 5px;
    color: ${c.profile.profile_links};
}

.profile-sp-comment > div {
    margin-top: 2px;
}

.profile-sp-comment-text {
	padding-left: 10px;
	color: ${c.profile.primary_txt};
    vertical-align: top;
}

.profile-sp-commentcontainer {
	margin-bottom: 8px;
}

/*The comment controls*/
.profile-sp-commentcontainer > a {
	margin-right: 2px;
    line-height: 13pt;
}

.profile-sp-comment-pic {
    float: right;
    padding-left: 8px;
}

.spot-comment-textarea {
	/*width: 250px;*/
    width: 100%;
	height: 65px;
	margin-bottom: 2px;
}

.spot-controls {
	margin-left: 2px;
}

.spot-controls a {
	margin-left: 2px;
}

.profile-right {
    text-align: right;
}

.profile-stretch {
    width: 100%;
}

.spotlight-timestamp {
    font-size: 10px;
}

.h-title a {
    text-decoration: none;
}

.h-title img {
	vertical-align: text-bottom;
}

.profile-pic {
	margin-bottom: 10px;
}

.fake-albumart {
	height: 78px;
	width: 80px;
	margin-left: 25px
}

.fake-enqueue {
	height: 15px;
	width: 20px;
}
