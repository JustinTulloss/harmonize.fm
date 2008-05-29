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

#downloadlink {
    margin-left: 37px;
}

#downloadlink a {
    color: ${c.profile.dark_txt};
    text-decoration: none;
}

#downloadlink a:hover {
    color: ${c.profile.click}
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

#spot_bg {
	position: absolute;
	z-index: 1;
	height: 100%;
	width: 100%;
	left: 0;
	top: 0;
}

#spot_content {
	margin-top: 10px;
	padding: 10px;
	background-color: white;
	border: solid 2px ${c.profile.dark_txt};
}

#spot_content h1, #spot_content h2 {
	margin-top: 0px;
	margin-bottom: 10px;
}

#spot_content tr {
	text-align: center;
}

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

td {
	margin: 0;
	padding: 0;
}

#spot_cancel {
	margin-left: 4px;
}

