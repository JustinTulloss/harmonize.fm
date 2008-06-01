var init_feedback;
(function() {
	var feedback_active = false;
	var feedback_template =
		'<h1>Send us your Feedback</h1><center><table id="feedback-content"><tr><td><textarea id="feedback-textarea"></textarea></td></tr><tr><td class="feedback-label">comment</td></tr><tr><td><input id="feedback-email"></input></td></tr><tr><td class="feedback-label">your email</td></tr><tr><td><button id="feedback-send">send</button><button id="feedback-cancel">cancel</button></td></tr></table></center>';
	function show_feedback(e) {
		e.preventDefault();

		if (!feedback_active) {
			feedback_active = true;

			show_dialog(feedback_template);
			Ext.get('feedback-cancel').on('click', hide_feedback);
			Ext.get('feedback-send').on('click', send_feedback);
		}
	}

	function hide_feedback() {
		feedback_active = false;
		hide_dialog();
	}

	init_feedback = function() {
		Ext.get('feedback-link').on('click', show_feedback);
	}

	function send_feedback() {
		var textarea = Ext.get('feedback-textarea');
		if (textarea.dom.value != '') {
			var emailInput = Ext.get('feedback-email');
			Ext.Ajax.request({
				url: '/player/feedback',
				params: { email: emailInput.dom.value,
						  feedback: textarea.dom.value},
				success: hide_feedback,
				failure: hide_feedback
			});
		}
	}
})();
