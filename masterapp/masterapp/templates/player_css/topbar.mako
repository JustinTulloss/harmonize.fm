/* vim:filetype=css
*/
#header {
	width: 100%;
    height: 74px;
    border: none;
    background: ${c.profile.top_bg};
}

#playcontrols {
    height: 24px;
    /*background: url('/images/controls-new.png');
    z-index: 30; */
    position: relative;
    padding: 0;
	margin-top: 1px;
	margin-bottom: 0;
	/*background-color: #A0ACC0;
	border: solid white 1px;
	*/
}

#play-img {
	height: 18px;
	width: 18px;
}

#next-img {
	height: 18px;
	width: 31px;
    background: transparent url('/images/controls-new.png') -18px -18px no-repeat;
}

#prev-img {
	height: 18px;
	width: 31px;
    background: transparent url('/images/controls-new.png') -18px 0 no-repeat;
}

.pause {
    background: transparent url('/images/controls-new.png') 0 -18px no-repeat;
}	

.play {
    background: transparent url('/images/controls-new.png') 0 0 no-repeat;
}

#playcontrols a {
    margin: 0;
    padding: 0;
    height: 22px;
	background-color: #A0ACC0;
}

#prevbutton {
	height: 22px;
	position: absolute;
	left: 35px;
	padding-top: 3px;
}

#nextbutton {
	position:absolute;
	left: 72px;
	padding-top: 3px;
	height: 22px;
}

#playbutton {
	width: 18px;
	height: 22px;
	padding-top: 3px;
	padding-left: 8px;
	position: absolute;
};

/*
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

*/
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
	height: 74px;
	float: left;
	z-index: 30;
	padding: 0;
}

#now-playing-title {
	color: white;
	font-size: 14px;
	margin-left: 5px;
}

#now-playing-artist {
	color: white;
	margin-left: 5px;
}

#now-playing-bar {
	height: 12px;
	background-color: white;
	border: 1px black solid;
	position: relative;
	margin-left: 3px;
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
