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

function FeedbackButton() {
	if (this == window)
		alert("FeedbackButton not called with new!");

	that = this;

	function show_feedback_box() {
		alert("Feedback box opened!");
	}

	var feedbackContainer = document.createElement('div');
	var feedbackButton = 
		new Ext.Toolbar.Button({text:'feedback', cls:'menuitem'});
	var feedbackButtonDom = document.getElementById(feedbackButton.getId());
		
	feedbackButton.on('click', show_feedback_box);
	feedbackContainer.appendChild(feedbackButtonDom);
}
