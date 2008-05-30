<%def name="render(entries)">
	<%def name="format_entry(entry)">
		<div class="blogentry">
			<div class="blogtitle"> ${entry.title} </div>
			<span class="blogbyline">by<span class="blogauthor"> ${entry.author} </span></span>
			<div class="blogcontent"> ${entry.entry} </div>
		</div>
	</%def>

    <div id="blog">
        % for entry in entries:
            ${format_entry(entry)}
        % endfor
    </div>
</%def>
