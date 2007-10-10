
body, html {
    height: 100%;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
    font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
    font-size: 12px;
    color: ${c.profile.primary_txt}
}

.instruction {
    text-align: center;
    margin: 0;
    display: table-cell;
    vertical-align: middle;
}

.middle {
    text-align: center;
    vertical-align: middle;
}

.control {
    vertical-align: middle;
    margin: 1em;
}

#top {
    height: 10%;
    min-height: 62px;
    max-height: 62px;
    background-image: url('/images/top-bg.png');
    background-repeat: repeat-x;
}

#controls {
    width: 16%;
    text-align: center;
}

#queue {
    float: left;
    width: 16%;
    min-width: 100px;
    height: 90%;
    padding: 0;
    margin: 0;
    display: table;
    vertical-align: middle;
	background-color: ${c.profile.queue_bg};
    border-right: 1px solid ${c.profile.border};
}

#browser {
    width: 100%;
}
