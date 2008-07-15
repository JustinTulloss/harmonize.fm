Ext.onReady(function() {
	var regex = /^(\w+)\/(\d+)(&(.*))?/;

	function enqueue(params) {
		var match = params.match(regex);
		if (!match) return;

		var type = match[1];
		var id = match[2];
		var friend_id = '';
		var source = 2;
		if (match[4]) {
			var decoded = Ext.urlDecode(match[4]);
			friend_id = decoded['Friend_id'] || friend_id;
			source = decoded['source'] || source;
		}
	
		function failure() {
			show_status_msg('Unable to enqueue music!');
		}
		function enqueue_result(response) {
			var record = untyped_record(response);
			record.set('Friend_id', friend_id);
			record.set('source', source);
			playlistmgr.enqueue([record]);
		}
		Ext.Ajax.request({
			url:'/metadata/'+type+'/'+id,
			success: enqueue_result,
			failure: failure,
			params: {friend: friend_id}
		});
	}

	urlm.register_action('enqueue', enqueue);
});
