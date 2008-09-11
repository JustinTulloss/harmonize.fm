var init_feedback;
(function() {
	var feedback_active = false;
	var feedback_template = new Ext.Template(
		'<h1>Send us your Feedback</h1>',
        '<center><table id="feedback-content"><tr>',
            '<td class="h-light-form">',
            '<textarea id="feedback-textarea" class="dlg-focus">',
            '</textarea></td>',
        '</tr><tr>',
            '<td class="feedback-label">comment</td>',
        '</tr><tr>',
            '<td class="h-light-form"><input id="feedback-email" value={email}></input>',
            '<input type="hidden" id="feedback-browser" value={browser}></input></td>',
        '</tr><tr>',
            '<td class="feedback-label">your email</td>',
        '</tr><tr>',
            '<td>',
                '<button id="feedback-cancel">cancel</button>',
                '<button id="feedback-send">send</button>',
            '</td>',
        '</tr></table></center>');
    feedback_template = feedback_template.compile();

	function show_feedback() {

		if (!feedback_active) {
			feedback_active = true;

			show_dialog(feedback_template.apply({
                browser:escape(get_browser_data()),
                email: global_config.email
            }));
			//show_dialog(feedback_template.apply('bleh'));
			Ext.fly('feedback-cancel').on('click', hide_feedback);
			Ext.fly('feedback-send').on('click', send_feedback);
		}
	}

	function hide_feedback() {
		feedback_active = false;
		hide_dialog();
	}

	init_feedback = function() {
		//Ext.get('feedback-link').on('click', show_feedback);
        urlm.register_action('feedback', show_feedback);
	};

	function send_feedback() {
		var textarea = Ext.get('feedback-textarea');
		if (textarea.dom.value) {
			var emailInput = Ext.get('feedback-email');
			var browser = Ext.get('feedback-browser');
			Ext.Ajax.request({
				url: '/player/feedback',
				params: { email: emailInput.dom.value,
						  feedback: textarea.dom.value,
						  browser: browser.dom.value},
				success: function() {
							hide_feedback();
							show_status_msg("Feedback Received!");},
				failure: hide_feedback
			});
		}
	}
})();
