/*
 * Ext JS Library 2.0
 * Copyright(c) 2006-2007, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

.x-window {
    zoom:1;
    background: white;
    border: 1px solid ${c.profile.light_form}
}
.x-window .x-resizable-handle {
    opacity:0;
    -moz-opacity:0;
    filter:alpha(opacity=0);
}

.x-window-proxy {
    background:${c.profile.queue_bg};
    border:1px solid #99bbe8;
    z-index:12000;
    overflow:hidden;
    position:absolute;
    left:0;top:0;
    display:none;
    opacity:.5;
    -moz-opacity:.5;
    filter:alpha(opacity=50);
}

.x-window-header {
    overflow:hidden;
    zoom:1;
}
.x-window-bwrap {
    z-index:1;
    position:relative;
    zoom:1;
}
.x-window-tl .x-window-header {
    color: ${c.profile.dark_txt};
    font-size: 16pt;
    padding:5px 0 4px 0;
}
.x-window-header-text {
    cursor:pointer;
}
.x-window-tc {
	overflow:hidden;
    zoom:1;
}
.x-window-tl {
	padding-left:6px;
    zoom:1;
    z-index:1;
    position:relative;
}
.x-window-tr {
	padding-right:6px;
}
.x-window-bc {
    zoom:1;
}
.x-window-bc .x-window-footer {
    padding-bottom:6px;
    zoom:1;
    font-size:0;
    line-height:0;
}
.x-window-bl {
	padding-left:6px;
    zoom:1;
}
.x-window-br {
	padding-right:6px;
    zoom:1;
}
.x-window-mc {
    padding:0;
    margin:0;
}

.x-window-ml {
	padding-left:6px;
    zoom:1;
}
.x-window-mr {
	padding-right:6px;
    zoom:1;
}
.x-panel-nofooter .x-window-bc {
	height:6px;
}
.x-window-body {
    overflow:hidden;
}
.x-window-bwrap {
    overflow:hidden;
}
.x-window-maximized .x-window-bl, .x-window-maximized .x-window-br,
    .x-window-maximized .x-window-ml, .x-window-maximized .x-window-mr,
    .x-window-maximized .x-window-tl, .x-window-maximized .x-window-tr {
    padding:0;
}
.x-window-maximized .x-window-footer {
    padding-bottom:0;
}
.x-window-maximized .x-window-tc {
    padding-left:3px;
    padding-right:3px;
    background-color:white;
}
.x-window-maximized .x-window-mc {
    border-left:0 none;
    border-right:0 none;
}
.x-window-tbar .x-toolbar, .x-window-bbar .x-toolbar {
    border-left:0 none;
    border-right: 0 none;
}
.x-window-bbar .x-toolbar {
    border-top:1px solid #99bbe8;
    border-bottom:0 none;
}
.x-window-draggable, .x-window-draggable .x-window-header-text {
    cursor:move;
}
.x-window-maximized .x-window-draggable, .x-window-maximized .x-window-draggable .x-window-header-text {
    cursor:default;
}
.x-window-body {
    background:transparent;
}
.x-panel-ghost .x-window-tl {
    border-bottom:1px solid #99bbe8;
}
.x-panel-collapsed .x-window-tl {
    border-bottom:1px solid #84a0c4;
}
.x-window-maximized-ct {
    overflow:hidden;
}
.x-window-maximized .x-resizable-handle {
    display:none;
}
.x-window-sizing-ghost ul {
    border:0 none !important;
}


.x-dlg-focus{
	-moz-outline:0 none;
	outline:0 none;
	width:0;
	height:0;
	overflow:hidden;
	position:absolute;
	top:0;
	left:0;
}
.x-dlg-mask{
	z-index:10000;
   display:none;
   position:absolute;
   top:0;
   left:0;
   -moz-opacity: 0.5;
   opacity:.50;
   filter: alpha(opacity=50);
   background-color:#CCC;
}

body.ext-ie6.x-body-masked select {
	visibility:hidden;
}
body.ext-ie6.x-body-masked .x-window select {
	visibility:visible;
}

.x-window-plain .x-window-mc {
    background: #CAD9EC;
    border-right:1px solid #DFE8F6;
    border-bottom:1px solid #DFE8F6;
    border-top:1px solid #a3bae9;
    border-left:1px solid #a3bae9;
}

.x-window-plain .x-window-body {
    border-left:1px solid #DFE8F6;
    border-top:1px solid #DFE8F6;
    border-bottom:1px solid #a3bae9;
    border-right:1px solid #a3bae9;
    background:transparent !important;
}

body.x-body-masked .x-window-plain .x-window-mc {
    background: ${c.profile.queue_bg};
}
