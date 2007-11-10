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

#home {
    text-align: center;
}

#mainlogo {
    width: 100%;
    text-align: center;
    vertical-align: middle;
    margin: 20px;
}

.mainmenu {
    color: #666;
    font-family: "Trebuchet", sans-serif;
    font-size: 16px;
    display: inline;
    margin-right: 20px;
    margin-left: 20px;
}

a.mainmenuitem:link {
    color: #666;
}

a.mainmenuitem:visited {
    color: #666;
}

a.mainmenuitem:hover {
    color: ${c.profile.click};
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
    #position: relative; /*IE fixes*/
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

a.bc_link {
    color:${c.profile.primary_txt};
}

a.bc_link:hover {
    color: ${c.profile.click};
}

.bc {
    display:inline;
}

#menu {
    display:block;
    height: 18px;
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
    display:block;
	width: 100%;
    height: 58px;
    z-index: 25;
    background-image: url('/images/top-bg.png');
    background-repeat: repeat-x;
    border: none;
}

#now-playing {
    /*
    position: relative;
    top: 10px;
    left: 300px;*/
    margin-top: 5px;
    margin-right: 400px;
    float:right;
    width: 40%;
    height: 60%;
    text-align: center;
    background-color: ${c.profile.oddrow_bg};
}

#np-title {
    display: block;
    font-weight: bold;
    font-size: 14px;
}

#np-info {
    display: block;
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
    margin-top: 0px;
}

#queue-container {
	background-color: ${c.profile.queue_bg};
}
#queue{
    /*
    position: absolute;
    top: 0px;
    left: 0;
    */
    z-index: 20;
    display:table;
    width:100%;
	height: 100%;
    min-width: 130px;
    vertical-align: middle;
}

#queue-menu {
    text-align: center;
}

a.queue-menu-item {
    color:${c.profile.primary_txt};
}

a.queue-menu-item:hover {
    color: ${c.profile.click};
}

.queue-menu-item {
    text-decoration: underline;
}
