/* vim:filetype=css
*/
#header {
	width: 100%;
    height: 72px;
    border: none;
    background: ${c.profile.top_bg};
}

#playcontrols {
    width: 92px;
    height: 18px;
    background: url('/images/controls-new.png');
    margin: 0;
	margin-left: 2px;
	margin-top: 2px;
    padding: 0;
    position: relative;
    z-index: 30;
}

#playcontrols li {
    margin: 0;
    padding: 0;
    list-style: none;
    position: absolute;
    top: 0;
}

#playcontrols li, #playcontrols a {
    height: 18px;
    display: block;
    outline: none;
}

#prevbutton {
    left: 28px;
    width: 29px;
}

#playbutton {
    left: 0px;
    width: 22px;
}

#nextbutton {
    left: 63px;
    width: 29px;
}

#prevbutton a:hover {
    background: transparent url('/images/controls-new.png') -28px -18px no-repeat;
}

#playbutton a:hover {
    background: transparent url('/images/controls-new.png') 0px -18px no-repeat;
}

#nextbutton a:hover {
    background: transparent url('/images/controls-new.png') -63px -18px no-repeat;
}

/*
#prevbutton a:active {
    background: transparent url('/images/controls.png') 0 -18px no-repeat;
}

#playbutton a:active {
    background: transparent url('/images/controls.png') -48px -85px no-repeat;
}

#nextbutton a:active {
    background: transparent url('/images/controls.png') -105px -85px no-repeat;
}
*/


.topmenu {
    font-size: 9px;
}

.menuitem {
    font-size: 9px;
    color: #FFFFFF;
}

.menuitem:hover button {
    color: ${c.profile.click};
}

#logo {
    position: absolute;
    right: 50px;
    bottom: -1pt;
}

#song-info-and-controls{
	width: 250px;
	float: left;
	padding: 2px;
	z-index: 30;
}

#now-playing-title {
	color: white;
	font-size: 14px;
	margin-left: 2px;
}

#now-playing-artist {
	color: white;
	margin-left: 2px;
}

#now-playing-bar {
	height: 12px;
	background-color: white;
	border: 1px black solid;
	position: relative;
}

#now-playing-progress {
	width: 0;
	height: 100%;
	background-color: #A9B7D3;
	position: absolute;
}

#now-playing-time {
	font-size: 10px;
	line-height: 11px;
	margin-left: 2px;
	position: absolute;
}
