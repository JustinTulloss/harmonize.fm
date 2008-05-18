/* vim:filetype=css
 */
.queue {
	background-color: ${c.profile.queue_bg};
}

.dragging {
    cursor: move;
}

.np-node {
    font-weight: bold;
    font-size: 9pt;
}

a.qn-text{
    cursor: default;
}

.qn-text{
    font-size: 9pt;
    color: ${c.profile.primary_txt};
}

.qn-delete {
    height: 15px;
    width: 15px;
    position: absolute;
    right: 1em;
    cursor: pointer;
}

#status {
    font-size: 9px;
}

#time {
    float: left;
    margin-left: 1em;
    margin-bottom: 0;
}

#timeline {
    position: relative;
    height: 10px;
    border: solid 1px ${c.profile.top_bg};
}

#time2 {
    float: right;
    margin-right: 1em;
    margin-bottom: 0;
}
