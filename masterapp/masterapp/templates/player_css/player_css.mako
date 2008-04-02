body, html {
    margin: 0;
    padding: 0;
    max-width: 100%;
    font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
    font-size: 12px;
    color: ${c.profile.primary_txt};
}

#mainlogo {
    width: 100%;
    text-align: center;
    vertical-align: middle;
    margin: 20px;
}

.instruction {
	background-color: ${c.profile.queue_bg};
    text-align: center;
    display: table-cell;
    vertical-align: middle;
    #position: relative; /*IE fixes*/
    #top: 50%;
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
