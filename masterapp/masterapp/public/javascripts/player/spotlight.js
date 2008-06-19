var spot_template = new Ext.Template(
		'<form id="spot_form">',
			'<h1 id="spot_form_title">Add Album to your Spotlight</h1>',
			'<h2>{album_name}&nbsp;-&nbsp;{artist_name}</h2>',
			'<center><table id="spot_controls"><tr><td><img id="spot_art" src="{album_art}" />',
			'<textarea id="spot_textarea"></textarea><div id="spot_comment">comment</div><div id="spot-error" class="dialog-warning"></div><br /></tr></td>',
			'<tr><td></td></tr>',
			'<tr><td><button id="spot_add">add</button>',
			'<button id="spot_cancel">cancel</button></center></td></tr>',
		'</table></form>');
		
var edit_spot_template = new Ext.Template(
		'<form id="spot_form">',
			'<h1 id="spot_form_title">Edit Spotlight</h1>',
			'<h2>{album_name}&nbsp;-&nbsp;{artist_name}</h2>',
			'<center><table id="spot_controls"><tr><td><img id="spot_art" src="{album_art}" />',
			'<textarea id="spot_textarea">{current_comment}</textarea><div id="spot_comment">comment</div><div id="spot-error" class="dialog-warning"></div><br /></tr></td>',
			'<tr><td></td></tr>',
			'<tr><td><button id="spot_change">change</button>',
			'<button id="spot_cancel">cancel</button></center></td></tr>',
		'</table></form>');
		
var delete_spot_template = new Ext.Template(
		'<form id="spot_form">',
			'<h1 id="spot_form_title">Delete Spotlight</h1>',
			'<h2>{album_name}&nbsp;-&nbsp;{artist_name}</h2>',
			'<center><table id="spot_controls"><tr><td><img id="spot_art" src="{album_art}" />',
			'<div class="spot-dlg-value">{current_comment}</div></tr></td>',
			'<tr><td>Are you sure?</td></tr>',
			'<tr><td>&nbsp;</td></tr>',
			'<tr><td><button id="spot_delete">delete</button>',
			'<button id="spot_cancel">cancel</button></center></td></tr>',
		'</table></form>');			

function show_spotlight(record,mode) {
    var spotlight;    
    if (mode == "add") {
    	spotlight = spot_template.apply( 
			    {album_name : record.get('Album_title'),
			     artist_name : record.get('Artist_name'),
			     album_art: record.get('Album_smallart')});
    } else if (mode == "edit" ){ 
        spotlight = edit_spot_template.apply(
                {album_name : record.get('Album_title'),
                artist_name : record.get('Artist_name'),
                album_art: record.get('Album_smallart'),
                current_comment: record.get('Spotlight_comment')});
    } else if (mode == "delete") {
        spotlight = delete_spot_template.apply(
                    {album_name: record.get('Album_title'),
                    artist_name: record.get('Artist_name'),
                    current_comment: record.get('Spotlight_comment'),
                    album_art: record.get('Album_smallart')   
                    }     
                );
        
    }
	show_dialog(spotlight);

	function add_spotlight(e) {
		e.preventDefault();
		var comment = document.getElementById('spot_textarea').value;
		if (comment.length <= 255) {
			Ext.Ajax.request({
				url:'/player/spotlight_album/'+record.get('Album_id'),
				success: function(response, options) {
				    if (response.responseText == "1") {
							hide_dialog(); 
							show_status_msg("Spotlight Added!");
					} else {
					    hide_dialog();
					    show_status_msg("Spotlight was NOT added.");
					}
				},
				failure: hide_dialog,
				params: {comment: comment}});
		}
		else {
			var warning = document.getElementById('spot-error');
			warning.innerHTML = 'Your comment is too long, please shorten it';
		}
	}
	
	function edit_spotlight(e) {
	    e.preventDefault();
	    var comment = document.getElementById('spot_textarea').value;
	    var id = record.get('id');
	    if (comment.length <= 255) {
	        Ext.Ajax.request({
                url:'/player/spotlight_album_edit',
                params: {comment: comment, spot_id: id},
                success: function(response, options) {
                    if (response.responseText == "True") {
                        hide_dialog();    
                        show_status_msg("Spotlight changed!");
                        urlm.invalidate_page();
                    } else hide_dialog();
                },
                failure: hide_dialog
	        });
	    } else {
	        var warning = document.getElementById('spot-error');
			warning.innerHTML = 'Your comment is too long, please shorten it';
	    }
	}
	
	function do_delete_spotlight(e) {
	    e.preventDefault();
        Ext.Ajax.request({
            url: 'player/delete_spotlight/'+ record.get('id'),
            success: function (response, options) {
                if (response.responseText == "True") {
                    hide_dialog();
                    show_status_msg("Spotlight deleted.");
                    urlm.invalidate_page();
                } else {
                    hide_dialog();
                    show_status_msg("Error deleting spotlight: bad server response.");
                }
            },
            failure: function (response, options) {
                hide_dialog();
                show_status_msg("Error deleting spotlight.");   
            }
        });
    }
    Ext.get('spot_cancel').on('click', prevent_default(hide_dialog));
	if (mode == "add") {
	    Ext.get('spot_add').on('click', prevent_default(add_spotlight));
	    Ext.get('spot_textarea').focus(); //This doesn't work the first time
	}
	else if (mode == "edit") {
	    Ext.get('spot_change').on('click', prevent_default(edit_spotlight));
	    Ext.get('spot_textarea').focus(); //This doesn't work the first time
	} else if (mode == "delete") {
	    Ext.get('spot_delete').on('click', prevent_default(do_delete_spotlight));
	}
}

function delete_spotlight(spot_id) {
    Ext.Ajax.request({
        url: 'metadata/find_spotlight_by_id/',
        params: {id: spot_id},
        success: 
            function(response, options) {
                if (response.responseText != "False") {
                    record = eval('(' + response.responseText + ')');
                    record = record.data[0];
                    record['id'] = spot_id;
                    record.get = (function(key) { return record[key];});
                    show_spotlight(record, "delete");
                } else show_status_msg("error parsing spotlight information");
            },        
        
        failure: function() {show_status_msg('error retrieving spotlight information');}
    });    
}

//Use a table to shrinkwrap content
var dialog_template = '<center><table id="dialog-window"><tr><td id="dialog-content"></td></tr></table></center>';

//Takes a string that consists of the dialogs content
function show_dialog(content) {
	var mainDiv = document.getElementById('dialog-bg');
	if (mainDiv) 
		var contentDiv = document.getElementById('dialog-content');
	else {
		var mainDiv = document.createElement('div');
		mainDiv.id = 'dialog-bg';
		mainDiv.innerHTML = dialog_template;
		document.getElementById('centerpanel').appendChild(mainDiv);
		var contentDiv = document.getElementById('dialog-content');
	}
	contentDiv.innerHTML = content;
}

function hide_dialog() {
	var dlg = Ext.get('dialog-bg');
	if (dlg)
		dlg.remove();
	//Not clear this is necessary in any cases now so it won't be the default
	//urlm.invalidate_page(); 
}

function show_status_msg(msg, keepshowing) {
	el = document.getElementById('status-box').firstChild;
	el.innerHTML = msg;
	el.style.visibility = 'visible';
	if (!keepshowing)
		setTimeout("hide_status_msg();", 5000);
}

function hide_status_msg() {
	el = document.getElementById('status-box').firstChild;
	el.style.visibility = 'hidden';
}

function prevent_default(fn) {
	return function(e) {
		e.preventDefault();
		fn();
	}
}
