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
    position: absolute;
    top: 20px;
    right: 25px;
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
    margin-left: 5px;
}

.blogauthor{
    font-weight: bold;
}

.blogcontent {
    padding-top: 5px;
    margin-left: 5px;
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
