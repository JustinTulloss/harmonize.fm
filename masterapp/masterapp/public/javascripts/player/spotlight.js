var spot_template = new Ext.Template(
		'<div id="spot_bg">',
		'<center><table><tr><td><form id="spot_form">',
		'<table id="spot_content">',
			'<tr><td><h1>Add Album to your Spotlight</h1></tr></td>',
			'<tr><td><h2>{album_name}&nbsp;-&nbsp;{artist_name}</h2></tr></td>',
			'<tr><td><center><table id="spot_controls"><tr><td><img id="spot_art" src="{album_art}" />',
			'<textarea id="spot_textarea"></textarea><div id="spot_comment">comment</div><br /></tr></td>',
			'<tr><td><button id="spot_add">add</button>',
			'<button id="spot_cancel">cancel</button></tr></td></table></center></td></tr>',
		'</table></form></center></td></tr></table></div>');

function show_spotlight(record) {
	var centerpanel = Ext.get('centerpanel');
	
	spot_template.append('centerpanel', 
			{album_name : record.data.Album_title,
			 artist_name : record.data.Artist_name,
			 album_art: record.json.Album_smallart});

	function add_spotlight(e) {
		Ext.Ajax.request({
			url:'/player/spotlight_album/'+record.data.Album_id,
			success: remove_spotlight,
			failure: remove_spotlight,
			params: {comment : document.getElementById('spot_textarea').value}});
		e.preventDefault();
	}

	Ext.get('spot_cancel').on('click', remove_spotlight);
	Ext.get('spot_add').on('click', add_spotlight);
}

function remove_spotlight(e) {
	Ext.get('spot_bg').remove();
}

