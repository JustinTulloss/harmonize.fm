var spot_template = new Ext.Template(
		'<form id="spot_form">',
			'<h1>Add Album to your Spotlight</h1>',
			'<h2>{album_name}&nbsp;-&nbsp;{artist_name}</h2>',
			'<center><table id="spot_controls"><tr><td><img id="spot_art" src="{album_art}" />',
			'<textarea id="spot_textarea"></textarea><div id="spot_comment">comment</div><br /></tr></td>',
			'<tr><td><button id="spot_add">add</button>',
			'<button id="spot_cancel">cancel</button></center></td></tr>',
		'</table></form>');

function show_spotlight(record) {
	var spotlight = spot_template.apply( 
			{album_name : record.data.Album_title,
			 artist_name : record.data.Artist_name,
			 album_art: record.json.Album_smallart});

	show_dialog(spotlight);

	function add_spotlight(e) {
		Ext.Ajax.request({
			url:'/player/spotlight_album/'+record.data.Album_id,
			success: hide_dialog,
			failure: hide_dialog,
			params: {comment:document.getElementById('spot_textarea').value}});
		e.preventDefault();
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
}
