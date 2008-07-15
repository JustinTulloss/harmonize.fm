body, html {
    margin: 0;
    padding: 0;
    max-width: 100%;
    font-family: "Lucida Sans Unicode", "Lucida Grande", "Lucida Sans", "Lucida", sans-serif;
    font-size: 12px;
    color: ${c.profile.primary_txt};
}

ul {
	margin-left: 0;
	padding-left: 30px;
}

#no-music {
    margin-left: 20px;
	background-color: ${c.profile.oddrow_bg};
	margin-bottom: 20px;
}

#no-music .content {
	padding-left: 25px;
}

#no-music h2 {
    font-size: 12pt;
	font-weight: normal;
	margin: 0;
	padding-bottom: 10px;
    font-family: "Lucida Sans Unicode", "Lucida Grande", "Lucida Sans", "Lucida", sans-serif;
}

#no-music ul {
	margin: 0;
	padding: 0;
	list-style-type: none;
}

#no-music li {
	margin-bottom: 5px;
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
	width: 100%;
}

table#home td {
	vertical-align: top;
	padding-right: 14px;
}

#home-sidebar {
	border-left: 1px solid ${c.profile.profile_border};
	padding-left: 14px;
}

#home-sidebar a {
    text-decoration: none;
	font-size: 12pt;
}

#home-sidebar-header {
    margin-top: 0px;
}

.home-group {
	border-bottom: solid 1px ${c.profile.profile_border};
	margin-bottom: 20px;
	padding-bottom: 20px;
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

.light-links a {
	color: ${c.profile.profile_links};
}

.light-links a:hover {
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
	margin-bottom: 17px;
	margin-top: 2px;
}

.feed_content {
	margin-left: 25px;
}

.feed_content h2 {
	margin-top: 0;
	color: ${c.profile.dark_txt};
	margin-bottom: 2px;
	font-size: 14px;
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

.feed-separator {
	border-bottom: solid 1px ${c.profile.profile_border};
	padding-left: 5px;
	margin-bottom: 5px;
	color: ${c.profile.profile_subtitle};
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
    top: 30px;
    left: 0;
}

#status-box span {
	background-color: ${c.profile.oddrow_bg};
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

.grid-actions a {
	margin-right: 2px;
}


#error-reload {
	float: right;
}

.favicon {
	vertical-align: text-top;
}
