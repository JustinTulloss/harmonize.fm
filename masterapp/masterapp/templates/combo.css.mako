/*
 * Ext JS Library 2.1
 * Copyright(c) 2006-2008, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

.x-combo-list {
    border: 1px solid ${c.profile.light_form};
    zoom:1;
    overflow:hidden;
}
.x-combo-list-inner {
    overflow:auto;
    background:white;
    position:relative; /* for calculating scroll offsets */
    zoom:1;
    overflow-x:hidden;
}
.x-combo-list-hd {
    font:bold 11px tahoma, arial, helvetica, sans-serif;
    color:#15428b;
    background-image: url(../images/default/layout/panel-title-light-bg.gif);
    border-bottom:1px solid #98c0f4;
    padding:3px;
}
.x-resizable-pinned .x-combo-list-inner {
    border-bottom:1px solid #98c0f4;
}
.x-combo-list-item {
    font:normal 12px tahoma, arial, helvetica, sans-serif;
    padding:2px;
    border:1px solid #fff;
    white-space: nowrap;
    overflow:hidden;
    text-overflow: ellipsis;
}
.x-combo-list .x-combo-selected{
    background: ${c.profile.oddrow_bg};
    cursor:pointer;
}
.x-combo-noedit{
    cursor:pointer;
}
.x-combo-list .x-toolbar {
    border-top:1px solid #98c0f4;
    border-bottom:0 none;
}

.x-combo-list-small .x-combo-list-item {
    font:normal 11px tahoma, arial, helvetica, sans-serif;
}
