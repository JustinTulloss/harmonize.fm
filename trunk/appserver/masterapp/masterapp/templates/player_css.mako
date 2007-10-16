body, html {
    height: 100%;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
    font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
    font-size: 12px;
    color: ${c.profile.primary_txt};
}

:focus {
    outline: 0;
}

.left {
    width: 16%;
}

.instruction {
    text-align: center;
    display: table-cell;
    vertical-align: middle;
    #position: relative;
    #top: 50%;
}

.middle {
    text-align: center;
    vertical-align: middle;
}

.control {
    vertical-align: middle;
    margin-top: 1em;
    margin-left: 1em;
    margin-right: 1em;
}

#top {
    position: absolute;
    top: 0;
    left: 0;
    height: 58px;
	width: 100%;
    z-index: 25;
    background-image: url('/images/top-bg.png');
    background-repeat: repeat-x;
    margin:0;
    border: none;
}

#controls {
    text-align: center;
    width: 16%;
}

#status {
    font-size: 9px;
    width: 16%;
}

#time {
    float: left;
    margin-left: 1em;
    margin-bottom: 0;
}

#timeline {
    position: relative;
    width: 113px;
    height: 13px;
	margin: 0 auto;
    background-image: url("/images/timeline-bg.png");
	background-position: center center;
    background-repeat: no-repeat;
}

#shuttle {
    position: absolute;
}

#time2 {
    float: right;
    margin-right: 1em;
    margin-bottom: 0;
}

#queue {
    position: absolute;
    top: 0px;
    left: 0;
    z-index: 20;
    width: 16%;
	height: 100%;
    min-width: 130px;
    margin: 0;
    display: table;
    vertical-align: middle;
	background-color: ${c.profile.queue_bg};
    border-right: 1px solid ${c.profile.border};
}

#browser {
    position: absolute;
    top: 58px;
    right: 0px;
    width: 84%;
    margin: 0;
    padding: 0;
}
