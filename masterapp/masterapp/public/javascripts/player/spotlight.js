var spot_template = new Ext.Template(
		'<form id="spot_form">',
			'<h1>Add Album to your Spotlight</h1>',
			'<h2>{album_name}&nbsp;-&nbsp;{artist_name}</h2>',
			'<center><table id="spot_controls"><tr><td><img id="spot_art" src="{album_art}" />',
			'<textarea id="spot_textarea"></textarea><div id="spot_comment">comment</div><div id="spot-error" class="dialog-warning"></div><br /></tr></td>',
			'<tr><td></td></tr>',
			'<tr><td><button id="spot_add">add</button>',
			'<button id="spot_cancel">cancel</button></center></td></tr>',
		'</table></form>');

function show_spotlight(record) {
	var spotlight = spot_template.apply( 
			{album_name : record.get('Album_title'),
			 artist_name : record.get('Artist_name'),
			 album_art: record.get('Album_smallart')});

	show_dialog(spotlight);

	function add_spotlight(e) {
		e.preventDefault();
		var comment = document.getElementById('spot_textarea').value;
		if (comment.length <= 255) {
			Ext.Ajax.request({
				url:'/player/spotlight_album/'+record.get('Album_id'),
				success: function() {
							hide_dialog(); 
							show_status_msg("Spotlight Added!");},
				failure: hide_dialog,
				params: {comment: comment}});
		}
		else {
			var warning = document.getElementById('spot-error');
			warning.innerHTML = 'Your comment is too long, please shorten it';
		}
	}

	Ext.get('spot_cancel').on('click', hide_dialog);
	Ext.get('spot_add').on('click', add_spotlight);
	Ext.get('spot_textarea').focus(); //This doesn't work the first time
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
