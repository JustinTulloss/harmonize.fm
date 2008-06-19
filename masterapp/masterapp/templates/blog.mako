<%def name="render(entries)">
	<%def name="format_entry(entry)">
		<div class="blogentry">
			<div class="h-title"> ${entry.title} </div>
			<span class="blogbyline">by<span class="blogauthor"> ${entry.author} </span>
	%	if entry.timestamp:
			on ${entry.timestamp.strftime('%b %d')}
	%	endif
 </span>
			<div class="blogcontent"> ${entry.entry} </div>
		</div>
	</%def>

    <div id="blog">
        <div class='h-subtitle'>News</div>
        % for entry in entries:
            ${format_entry(entry)}
        % endfor
    </div>
</%def>

%	if hasattr(c, 'main') and c.main:
	${render(c.entries)}
%	endif
