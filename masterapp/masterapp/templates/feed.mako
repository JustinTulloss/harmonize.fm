<%!
	from masterapp.model import BlogEntry, Spotlight
	from simplejson import dumps
%>

<%def name="render(entries)">
	<%def name="blog_feed(entry)">
		<div class="feed_content">
			<h4>${entry.author} wrote a new blog post</h4>
			<a href="#/player/blog/${entry.id}">read more...</a>
		</div>
	</%def>

	<%def name="spotlight_feed(entry)">
		<%
		max_quote_len = 175
		%>

		<img src="/images/enqueue.png" onclick="enqueue_album(${entry.album.id});" />
		<div class="feed_content">
			<h4>${entry.user.get_firstname()} 
				added a Spotlight on ${entry.album.title}</h4>
			<table class="spotlight_feed_info"><tr>
				<!--td><img src="/images/enqueue.png" /></td-->
				<td><img src="${entry.album.smallart}" /></td>
				<td class="spotlight_feed_comment">
	%	if len(entry.comment) < max_quote_len:
				${entry.comment}
	%	else:
				${entry.comment[:max_quote_len] + '...'}	
	%	endif
				</td>
			</tr></table>
		</div>
	</%def>

	<div id="news_feed">
	<%
		type_table = {
			BlogEntry : blog_feed,
			Spotlight : spotlight_feed
		}
	%>
	%	for entry in entries:
			<div class="feed_entry">
			${type_table[type(entry)](entry)}
			</div>
	%	endfor
	</div>
</%def>

