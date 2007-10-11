<%doc>
    This is the css for the yahoo datatable used as the
    main table of tag data.
</%doc>

/*foundational css*/
.yui-dt-table th, .yui-dt-table td {
    overflow:hidden;
}

th .yui-dt-header {
    position:relative;
}

th .yui-dt-label {
    position:relative;
}

th .yui-dt-resizer {
    position:absolute;
    margin-right:-6px;
    right:0;
    bottom:0;
    width:6px;
    height:100%;
    cursor:w-resize;
    cursor:col-resize;
}

/* foundational scrolling css */
.yui-dt-scrollable  {
    *overflow-y:auto; /* for ie */
}
.yui-dt-scrollable  thead {
    display:block; /* for safari and opera */
}
.yui-dt-scrollable thead tr {
    position:relative;  /* for ie */
}
.yui-dt-scrollbody {
    display:block; /* for safari and opera */
    overflow:auto; /* for gecko */
}

.yui-dt-editor {
    position:absolute;z-index:9000;
}


/* basic skin styles */
.yui-skin-sam .yui-dt-table {
    margin:0;
    padding:0;
    width: 100%;
    font-size:inherit;
    border-collapse:collapse;
    border: none;
}
.yui-skin-sam .yui-dt-table caption {padding-bottom:1em;text-align:left;}
.yui-skin-sam .yui-dt-table th {
    background-color: ${c.profile.queue_bg};
}
.yui-skin-sam .yui-dt-table th,
.yui-skin-sam .yui-dt-table th a {
    font-weight:bold;
    text-decoration:none;
    color:${c.profile.primary_txt}; /* header text */
    vertical-align:bottom;
}
.yui-skin-sam .yui-dt-table th,
.yui-skin-sam .yui-dt-table td {
    padding:4px 10px 4px 10px; /* cell padding */
    border-right:1px solid ${c.profile.border}; /* inner column border */
}
.yui-skin-sam .yui-dt-table td {
    white-space:nowrap;
    text-align:left;
}
.yui-skin-sam .yui-dt-table th.yui-dt-last,
.yui-skin-sam .yui-dt-table td.yui-dt-last {
    #border-right:1px solid ${c.profile.border}; /* outer border */
}
.yui-skin-sam .yui-dt-list td {
    border-right:none; /* disable inner column border in list mode */
}
.yui-skin-sam .yui-dt-table thead {
    #border:1px solid ${c.profile.border}; /* outer border */
}
/*
.yui-skin-sam .yui-dt-table tbody {
    border-left:1px solid ${c.profile.border};
    border-right:1px solid ${c.profile.border};
    border-bottom:1px solid ${c.profile.border}; /* outer border */
}*/

/* messaging */
.yui-skin-sam .yui-dt-loading {
    background-color:#FFF;
}

.yui-skin-sam .yui-dt-loading {
    background-color:#FFF;
}

/* sortable columns */
.yui-skin-sam .yui-dt-sortable {
    cursor:pointer;
}
.yui-skin-sam th.yui-dt-sortable {
    padding-right:5px; /* room for arrow */
}
.yui-skin-sam th.yui-dt-sortable .yui-dt-label {
    margin-right:15px; /* room for arrow */
}
.yui-skin-sam th.yui-dt-asc,
.yui-skin-sam th.yui-dt-desc {
}
.yui-skin-sam th.yui-dt-asc .yui-dt-header {
    background:url('/images/dt-arrow-up.png') no-repeat right; 
}
.yui-skin-sam th.yui-dt-desc .yui-dt-header {
    background:url('/images/dt-arrow-dn.png') no-repeat right; 
}

/* editing */
.yui-dt-editable {
    cursor:pointer;
}
.yui-dt-editor {
    text-align:left;
    background-color:#F2F2F2;
    border:1px solid #808080;
    padding:6px;
}
.yui-dt-editor label {
    padding-left:4px;padding-right:6px;
}
.yui-dt-editor .yui-dt-button {
    padding-top:6px;text-align:right;
}
.yui-dt-editor .yui-dt-button button {
    background:url(../../../../assets/skins/sam/sprite.png) repeat-x 0 0;
    border:1px solid #999;
    width:4em;height:1.8em;
    margin-left:6px;
}
.yui-dt-editor .yui-dt-button button.yui-dt-default {
    background:url(../../../../assets/skins/sam/sprite.png) repeat-x 0 -1400px;
    background-color: #5584E0;
    border:1px solid #304369;
    color:#FFF
}
.yui-dt-editor .yui-dt-button button:hover {
    background:url(../../../../assets/skins/sam/sprite.png) repeat-x 0 -1300px;
    color:#000;
}
.yui-dt-editor .yui-dt-button button:active {
    background:url(../../../../assets/skins/sam/sprite.png) repeat-x 0 -1700px;
    color:#000;
}

/* striping */
.yui-skin-sam tr.yui-dt-even { background-color:#FFF; } /* white */
.yui-skin-sam tr.yui-dt-odd { background-color:${c.profile.oddrow_bg}; } /* light orange */
.yui-skin-sam tr.yui-dt-even td.yui-dt-asc,
.yui-skin-sam tr.yui-dt-even td.yui-dt-desc { background-color:${c.profile.oddrow_bg}; }
.yui-skin-sam tr.yui-dt-odd td.yui-dt-asc,
.yui-skin-sam tr.yui-dt-odd td.yui-dt-desc { background-color:${c.profile.sortoddrow_bg}; }

/* disable striping in list mode */
.yui-skin-sam .yui-dt-list tr.yui-dt-even { background-color:#FFF; } /* white */
.yui-skin-sam .yui-dt-list tr.yui-dt-odd { background-color:#FFF; } /* white */
.yui-skin-sam .yui-dt-list tr.yui-dt-even td.yui-dt-asc,
.yui-skin-sam .yui-dt-list tr.yui-dt-even td.yui-dt-desc { background-color:#EDF5FF; } /* light blue sorted */
.yui-skin-sam .yui-dt-list tr.yui-dt-odd td.yui-dt-asc,
.yui-skin-sam .yui-dt-list tr.yui-dt-odd td.yui-dt-desc { background-color:#EDF5FF; } /* light blue sorted */

/* highlighting */
.yui-skin-sam tr.yui-dt-highlighted,
.yui-skin-sam tr.yui-dt-highlighted td.yui-dt-asc,
.yui-skin-sam tr.yui-dt-highlighted td.yui-dt-desc,
.yui-skin-sam tr.yui-dt-even td.yui-dt-highlighted,
.yui-skin-sam tr.yui-dt-odd td.yui-dt-highlighted {
    cursor:pointer;
    background-color:#B2D2FF; /* med blue hover */
}

/* enable highlighting in list mode */
.yui-skin-sam .yui-dt-list tr.yui-dt-highlighted,
.yui-skin-sam .yui-dt-list tr.yui-dt-highlighted td.yui-dt-asc,
.yui-skin-sam .yui-dt-list tr.yui-dt-highlighted td.yui-dt-desc,
.yui-skin-sam .yui-dt-list tr.yui-dt-even td.yui-dt-highlighted,
.yui-skin-sam .yui-dt-list tr.yui-dt-odd td.yui-dt-highlighted {
    cursor:pointer;
    background-color:#B2D2FF; /* med blue  hover */
}

/* selection */
.yui-skin-sam tr.yui-dt-selected td,
.yui-skin-sam tr.yui-dt-selected td.yui-dt-asc,
.yui-skin-sam tr.yui-dt-selected td.yui-dt-desc {
    background-color:#426FD9; /* bright blue selected row */
    color:#FFF;
}
.yui-skin-sam tr.yui-dt-even td.yui-dt-selected,
.yui-skin-sam tr.yui-dt-odd td.yui-dt-selected {
    background-color:#446CD7; /* bright blue selected cell */
    color:#FFF;
}

/* enable selection in list mode */
.yui-skin-sam .yui-dt-list tr.yui-dt-selected td,
.yui-skin-sam .yui-dt-list tr.yui-dt-selected td.yui-dt-asc,
.yui-skin-sam .yui-dt-list tr.yui-dt-selected td.yui-dt-desc {
    background-color:#426FD9; /* bright blue selected row */
    color:#FFF;
}
.yui-skin-sam .yui-dt-list tr.yui-dt-even td.yui-dt-selected,
.yui-skin-sam .yui-dt-list tr.yui-dt-odd td.yui-dt-selected {
    background-color:#446CD7; /* bright blue selected cell */
    color:#FFF;
}

/* pagination */
.yui-skin-sam .yui-dt-paginator {
    display:block;margin:6px 0;white-space:nowrap;
}
.yui-skin-sam .yui-dt-paginator .yui-dt-first,
.yui-skin-sam .yui-dt-paginator .yui-dt-last,
.yui-skin-sam .yui-dt-paginator .yui-dt-selected {
    padding:2px 6px;
}
.yui-skin-sam .yui-dt-paginator a.yui-dt-first,
.yui-skin-sam .yui-dt-paginator a.yui-dt-last {
    text-decoration:none;
}
.yui-skin-sam .yui-dt-paginator .yui-dt-previous,
.yui-skin-sam .yui-dt-paginator .yui-dt-next {
    display:none;
}
.yui-skin-sam a.yui-dt-page {
    border:1px solid #CBCBCB;
    padding:2px 6px;
    text-decoration:none;
}


