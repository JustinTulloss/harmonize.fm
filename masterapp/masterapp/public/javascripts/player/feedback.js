var show_feedback_box;

(function() {
	var current_window = null;

	show_feedback_box = function() {
		if (!current_window) {
			current_window = new Ext.Window({
				title:'feedback',
				closable:true,
				height:300,
				width:300});
			current_window.expand();
			current_window.setVisible(true);
		}
	}
})();

function feedbackButton() {
	//if (this == window)
	//	alert("FeedbackButton not called with new!");

	//that = this;

	var active = false;

	function show_feedback_box() {
		feedbackBox.dom.style.display = 'block';
		feedbackButton.addClass('feedbackActive');
		active = true;
	}

	function hide_feedback_box() {
		feedbackBox.dom.style.display = 'none';
		feedbackButton.removeClass('feedbackActive');
		active = false;
	}

	function toggle_feedback_box() {
		if (active) hide_feedback_box();
		else show_feedback_box();
	}

	function set_state(new_state) {
		current_state.dom.style.display = 'none';
		new_state.dom.style.display = 'block';
		current_state = new_state;
	}

	function send_feedback() {
		if (textarea.dom.value != '') {
			set_state(sendingDiv);
			Ext.Ajax.request({
				url: '/player/feedback',
				params: { email: emailInput.dom.value,
						  feedback: textarea.dom.value},
				success: function() { set_state(successDiv); },
				failure: function() { set_state(failureDiv); }
			});
		}
	}

	function cancel_feedback() {
		emailInput.dom.value = '';
		textarea.dom.value = '';
		hide_feedback_box();
	}

	var feedbackContainer = Ext.get(document.createElement('div'));
	feedbackContainer.dom.id = 'feedbackContainer';

	var feedbackButton = Ext.get(document.createElement('div'));
	//	new Ext.Button({text:'feedback', cls:'menuitem'});
	
	feedbackButton.dom.className = 'menuitem';
	feedbackButton.dom.style.paddingLeft = '2px';
	feedbackButton.dom.style.paddingRight = '4px';
	feedbackButton.dom.innerHTML = 'feedback';
	
	feedbackButton.on('click', toggle_feedback_box);
	feedbackContainer.appendChild(feedbackButton);

	var positioningDiv = Ext.get(document.createElement('div'));
	positioningDiv.dom.style.position = 'relative';

	var feedbackBox = Ext.get(document.createElement('div'));
	feedbackBox.dom.id = 'feedbackBox';
	feedbackBox.dom.style.position = 'fixed';
	feedbackBox.dom.style.right = '3px';
	feedbackBox.dom.style.display = 'none';
	Ext.get(feedbackBox).addClass('feedbackActive');

	positioningDiv.appendChild(feedbackBox);
	feedbackContainer.appendChild(positioningDiv);

	var form = Ext.get(document.createElement('form'));
	var textarea = Ext.get(document.createElement('textarea'));
	textarea.dom.style.width = '100%';
	textarea.dom.setAttribute('wrap', 'hard');
	form.appendChild(textarea);

	var emailHeader = Ext.get(document.createElement('div'));
	emailHeader.dom.style.textAlign = 'right';
	emailHeader.dom.innerHTML = 'your email';
	form.appendChild(emailHeader);

	var emailInput = Ext.get(document.createElement('input'));
	emailInput.dom.style.width = '100%';
	form.appendChild(emailInput);

	var formControls = Ext.get(document.createElement('div'));
	formControls.dom.id = 'feedbackFormControls';

	var cancelLink = Ext.get(document.createElement('a'));
	cancelLink.dom.innerHTML = 'cancel';
	cancelLink.addClass('menuitem');
	cancelLink.dom.style.marginRight = '4px';
	cancelLink.on('click', cancel_feedback);
	formControls.appendChild(cancelLink);

	var sendLink = Ext.get(document.createElement('a'));
	sendLink.dom.innerHTML = 'send';
	sendLink.addClass('menuitem');
	sendLink.on('click', send_feedback);
	formControls.appendChild(sendLink);

	form.appendChild(formControls);

	feedbackBox.appendChild(form);

	var sendingDiv = Ext.get(document.createElement('div'));
	sendingDiv.dom.style.display = 'none';
	sendingDiv.dom.innerHTML = '<div style="text-align:left">sending...</div>';
	feedbackBox.appendChild(sendingDiv);

	function reset_feedback_box() {
		cancel_feedback();
		set_state(form);
	}

	var successDiv = Ext.get(document.createElement('div'));
	successDiv.dom.style.display = 'none';
	successDiv.dom.innerHTML = '<div style="text-align:left;">feedback received!</div>';
	var closeButton = Ext.get(document.createElement('a'));
	closeButton.dom.innerHTML = 'close';
	closeButton.addClass('menuitem');
	closeButton.on('click', reset_feedback_box);
	successDiv.appendChild(closeButton);
	feedbackBox.appendChild(successDiv);

	var failureDiv = Ext.get(document.createElement('div'));
	failureDiv.dom.style.display = 'none';
	//var failureMessage = document.createElement('p');
	failureDiv.dom.innerHTML = '<div style="text-align:left; white-space:normal;">Sorry, but the feedback system is temporarily unavailable, but feel free to email us at <a href="mailto:feedback@harmonize.fm">feedback@harmonize.fm</a></div>';
	var fcloseButton = Ext.get(document.createElement('a'));
	fcloseButton.dom.innerHTML = 'close';
	fcloseButton.addClass('menuitem');
	fcloseButton.on('click', reset_feedback_box);
	failureDiv.appendChild(fcloseButton);
	feedbackBox.appendChild(failureDiv);


	var current_state = form;

	return feedbackContainer.dom;
}
