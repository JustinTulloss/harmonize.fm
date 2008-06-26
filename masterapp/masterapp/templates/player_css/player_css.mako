body, html {
    margin: 0;
    padding: 0;
    max-width: 100%;
    font-family: "Lucida Sans Unicode", "Lucida Grande", "Lucida Sans", "Lucida", sans-serif;
    font-size: 12px;
    color: ${c.profile.primary_txt};
}

#no_music {
    margin-left: 12px;
}

#no_music h2{
    color: ${c.profile.dark_txt};
    font-family: "Lucida Sans Unicode", "Lucida Grande", "Lucida Sans", "Lucida", sans-serif;
}

#no_music a {
    color: ${c.profile.dark_txt};
}

#no_music a:hover {
    color: ${c.profile.click};
}

#mainlogo {
    position: absolute;
    right: 15px;
    bottom: 24px;
}

#blog {
    margin: 10px 20px 10px 20px;
}

#home {
	padding-top: 10px;
}

#home-sidebar {
    margin-right: 56px;
	font-size: 11pt;
	border-left: 1px solid ${c.profile.profile_border};
	padding-left: 8px;
}

#home-sidebar a {
    color: ${c.profile.dark_txt};
    text-decoration: none;
}

#home-sidebar div {
	margin-bottom: 2px;
}

#home-sidebar a:hover {
    color: ${c.profile.click}
}

#home-sidebar-header {
    margin-top: 0px;
}

#home-bg {
	float: right;
	background-color:white;
	padding-left: 8px;
}

.blogentry {
    padding-bottom: 15px;
}

.blogbyline{
    margin-left: 10px;
    color: ${c.profile.profile_links};
}

.blogcontent {
    padding-top: 5px;
    margin-left: 10px;
    width: 80%;
}

a.bc_link {
    color:${c.profile.dark_txt};
}

a.bc_link:hover {
    color: ${c.profile.click};
}

.bc {
    position: relative;
    bottom: 0;
    display:inline;
    font-size: 14px;
    color: ${c.profile.dark_txt};
}

.searchfield {
    position: absolute;
    right: 19px;
    top: 15px;
}

#bccontent {
	margin-top: 19px;
	margin-left: 16px;
}

#dialog-bg {
	position: absolute;
	z-index: 1;
	height: 100%;
	width: 100%;
	left: 0;
	top: 0;
	overflow: auto;
}

#dialog-window {
	margin-top: 10px;
	padding: 10px;
	background-color: white;
	border: solid 1px ${c.profile.light_form};
}

#dialog-content {
	text-align: center;
}

.dialog-content h1, .dialog-content h2 {
	margin-top: 0px;
	margin-bottom: 10px;
	text-align: center;
    color: ${c.profile.dark_txt};
}

.dialog-warning {
	color: red;
}

table td, table th {
	padding: 0;
}

table {
	border-spacing: 0;
}

#news_feed {
	margin-left: 20px;
}

#news_feed h1 {
	font-weight: normal;
	border-bottom: solid 1px ${c.profile.profile_border};
	margin: 0;
}

.feed_entry {
	margin-bottom: 2px;
}

.feed_content {
	margin-left: 25px;
}

.feed_content h4 {
	color: ${c.profile.dark_txt};
	margin-bottom: 2px;
	font-size: 11pt;
	font-weight: normal;
}

.feed_content a {
	color: ${c.profile.dark_txt};
	text-decoration: none;
}

.feed_content a:hover {
    color: ${c.profile.click};
	text-decoration: underline;
}

.feed_entry img {
	float: left;
	margin-top: 2px;
}

.blog_feed_comment {
	color: #777;
}

.spotlight_feed_comment {
	vertical-align: top;
	color: #777;
	padding-left: 7px;
	width: 250px;
}

.spotlight_feed_info {
	padding: 0;
}

#status-box {
	position: absolute;
	width: 100%;
	margin-top: 3px;
	text-align: center;
}

#status-box span {
	background-color: #D8DEEB;
    color: ${c.profile.dark_txt};
	padding: 3px 5px;
	visibility: hidden;
}

.content-container {
	height: 100%;
	overflow: auto;
}
.fblogin {
    width: 646px;
    height: 436px;
}

.grid-actions > img {
	margin-left: 1px;
	margin-right: 1px;
}

#shuffle-playqueue {
    margin-left: 15px;
}
