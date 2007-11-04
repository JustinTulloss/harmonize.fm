body, html {
    height: 100%;
    margin: 0;
    padding: 0;
    max-width: 100%;
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

.menuitem {
    display: inline;
    margin: .5em;
    font-size: 10px;
}

a.menuitem:link {
    color: ${c.profile.menu_txt};
}

a.menuitem:visited {
    color: ${c.profile.menu_txt};
}

a.menuitem:hover {
    color: ${c.profile.click};
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

.bc {
    display:inline;
}

.bc_link{
    display: inline;
}
    

#menu {
    position: absolute;
    top: 0px;
    height: 15px;
    width:100%;
    z-index:23;
    background: #486BAA;
    text-align: center;
}

#searchbar {
    color: ${c.profile.menu_txt};
    float: right;
    width: 130px;
    height: 100%;
    font-size: 10px;
    background-image: url('/images/searchbar.png');
    background-repeat: no-repeat;
    margin-right: 2em;
    padding-left: 5px;
    text-align: left;
}

#searchbar:focus {
    background-image: url('/images/searchbar_over.png');
}

#top {
    position: absolute;
    top: 15px;
    left: 0;
    height: 58px;
	width: 100%;
    z-index: 25;
    background-image: url('/images/top-bg.png');
    background-repeat: repeat-x;
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

#breadcrumb {
    float:right;
    width:84%;
    margin-top: 40px;
}

#queue{
    position: absolute;
    top: 0px;
    left: 0;
    padding-top: 80px;
    z-index: 20;
    display:table;
    width: 16%;
	height: 100%;
    min-width: 130px;
    vertical-align: middle;
	background-color: ${c.profile.queue_bg};
    border-right: 1px solid ${c.profile.border};
}

#browser {
    position: absolute;
    top: 73px;
    right: 0px;
    width: 84%;
    margin: 0;
    padding: 0;
}


