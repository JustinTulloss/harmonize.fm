body, html {
    margin: 0;
    padding: 0;
    max-width: 100%;
    font-family: "Lucida Sans Unicode", "Lucida Grande", "Lucida Sans", "Lucida", sans-serif;
    font-size: 12px;
    color: ${c.profile.primary_txt};
}

#mainlogo {
    position: absolute;
    right: 15px;
    bottom: 24px;
}

#blog {
    margin-top: 5pt;
    margin-left: 20pt;
    width: 80%;
}

#home-container {
	height: 100%;
	overflow: auto;
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
	border-botton: 1px solid $777;
	font-size: 16pt;
	color: ${c.profile.profile_subtitle};
	border-bottom: solid 1px ${c.profile.profile_border};
}

#home-bg {
	float: right;
	background-color:white;
	padding-left: 8px;
}

.blogtitle {
    font-size: 16pt;
    font-weight: bold;
    color: ${c.profile.dark_txt};
}

.blogentry {
    padding: 10px;
}

.blogbyline{
    margin-left: 10px;
}

.blogauthor{
    font-weight: bold;
}

.blogcontent {
    padding-top: 5px;
    margin-left: 10px;
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
    position: relative;
    left: 19px;
    top: 16px;
    display: inline;
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
	border: solid 2px ${c.profile.dark_txt};
}

#dialog-content {
	text-align: center;
}

#dialog-content h1, #dialog-content h2 {
	margin-top: 0px;
	margin-bottom: 10px;
	text-align: center;
}

/*
#spot_content tr {
	text-align: center;
}
*/

#spot_form textarea {
	height: 72px;
	width: 230px;
	margin: 0;
	margin-left: 4px;
}

#spot_comment {
	font-size: 12px;
	line-height: 12px;
}

#spot_form {
	text-align: right;
	overflow:auto;
}

#spot_art {
	float:left;
}

#spot_controls tr {
	text-align: right;
}

table td, table th {
	padding: 0;
}

table {
	border-spacing: 0;
}

#spot_cancel {
	margin-left: 4px;
}

#news_feed {
	margin-left: 12px;
	overflow: auto;
}

#news_feed h1 {
	color: ${c.profile.profile_subtitle};
	font-size: 16pt;
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
