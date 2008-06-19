/* vim:filetype=css
*/
#top-panel {
	z-index: 2;
}

#centerpanel {
	z-index: 0;
}

#queuepanel {
	z-index: 0;
}

#header {
	width: 100%;
    height: 74px;
    border: none;
    background: ${c.profile.top_bg};
}

#playcontrols {
    height: 24px;
    position: relative;
    padding: 0;
	margin-top: 1px;
	margin-bottom: 0;
}

.pcontrol {
	cursor: pointer;
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

#nextbutton:hover #next-img {
    background: transparent url('/images/controls-new.png') -18px -54px no-repeat;
}

#prev-img {
	height: 18px;
	width: 31px;
    background: transparent url('/images/controls-new.png') -18px 0 no-repeat;
}

#prevbutton:hover #prev-img {
    background: transparent url('/images/controls-new.png') -18px -36px no-repeat;
}

.pause {
    background: transparent url('/images/controls-new.png') 0 -18px no-repeat;
}	
#playbutton:hover .pause {
    background: transparent url('/images/controls-new.png') 0px -54px no-repeat;
}

.play {
    background: transparent url('/images/controls-new.png') 0 0 no-repeat;
}
#playbutton:hover .play {
    background: transparent url('/images/controls-new.png') 0px -36px no-repeat;
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

#topmenu {
	text-align: right;
}

#topmenu a {
    font-size: 13px;
    color: #FFFFFF;
	text-decoration: none;
	margin-right: 5px;
}

#topmenu *:hover {
    color: ${c.profile.click};
	text-decoration: none;
}

#topmenu *:focus {
	outline: none;
}

#feedback-link {
	position: relative;
}

.feedbackActive {
	background-color: #A0ACC0;
}

#feedback-content {
    width: 100%;
}

#feedback-content td {
	text-align: right;
}

#feedback-email {
	width: 98%;
}
#feedback-textarea {
	width: 98%;
    height: 100pt;
}
#feedback-cancel {
	margin-left: 5px;
}

.feedback-label {
	padding-bottom: 9px;
	line-height: 100%;
}

#feedbackBox {
	padding: 5px;
	width: 190px;
    font-size: 13px;
	font-family: tahoma,verdana,helvetica,sans-serif;
    color: #FFFFFF;
	text-align:right;

	position: fixed;
	right: 2px;
	display: none;
	z-index: 1
}

#feedbackContainer {
	height: 21px;
	vertical-align: middle;
}

#logo {
    position: absolute;
    right: 50px;
    bottom: 0px;
}

#logo img{
    border: none;
}

#song-info-and-controls{
	height: 74px;
	float: left;
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
	width: 250px;
	height: 12px;
	background-color: white;
	border: 1px white solid;
	position: relative;
	margin-left: 3px;
	visibility: hidden;
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

#volume {
	position: absolute;
	left: 132px;
	top: 0px;
}

#no-volume {
	position: absolute;
	left: 118px;
	top: 6px;
    background: transparent url('/images/controls-new.png') -60px -21px no-repeat;
	height: 14px;
	width: 11px;
}

#full-volume {
	position: absolute;
	left: 193px;
	top: 6px;
    background: transparent url('/images/controls-new.png') -71px -21px no-repeat;
	height: 14px;
	width: 19px;
}


