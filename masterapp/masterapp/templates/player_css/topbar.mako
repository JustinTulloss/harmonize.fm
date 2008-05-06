#header {
	width: 100%;
    height: 60px;
    border: none;
    background: ${c.profile.top_bg};
}

#playcontrols {
    width: 149px;
    height: 41px;
    background: url('/images/controls.png');
    margin: 0;
    padding: 0;
    position: relative;
    left: 4%;
    top: -8px;
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
    height: 41px;
    display: block;
    outline: none;
}

#prevbutton {
    left: 0;
    width: 47px;
}

#playbutton {
    left: 48px;
    width: 55px;
}

#nextbutton {
    left: 105px;
    width: 47px;
}

#prevbutton a:hover {
    background: transparent url('/images/controls.png') 0 -43px no-repeat;
}

#playbutton a:hover {
    background: transparent url('/images/controls.png') -48px -43px no-repeat;
}

#nextbutton a:hover {
    background: transparent url('/images/controls.png') -105px -43px no-repeat;
}

#prevbutton a:active {
    background: transparent url('/images/controls.png') 0 -85px no-repeat;
}

#playbutton a:active {
    background: transparent url('/images/controls.png') -48px -85px no-repeat;
}

#nextbutton a:active {
    background: transparent url('/images/controls.png') -105px -85px no-repeat;
}


.topmenu {
    background: ${c.profile.top_bg};
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

