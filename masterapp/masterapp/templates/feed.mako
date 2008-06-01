<%!
	from masterapp.model import BlogEntry, Spotlight
	from simplejson import dumps
%>

<%def name="render(entries)">

	<%def name="blog_feed(entry)">
		<div class="feed_content">
			<h4>${entry.author} wrote a new blog post</h4>
			<div class="blog_feed_comment">
				${quote_comment(entry.entry, 60)}</div>
			<a href="#/player/blog/${entry.id}">read more...</a>
		</div>
	</%def>

	<%def name="spotlight_feed(entry)">

		<img src="/images/enqueue.png" onclick="enqueue_album(${entry.album.id}, ${entry.uid});" />
		<div class="feed_content">
			<h4>${entry.user.get_firstname()} 
				added a Spotlight on ${entry.album.title}</h4>
			<table class="spotlight_feed_info"><tr>
				<!--td><img src="/images/enqueue.png" /></td-->
				<td><img src="${entry.album.smallart}" /></td>
				<td class="spotlight_feed_comment">
				${quote_comment(entry.comment, 175)}
				</td>
			</tr></table>
		</div>
	</%def>

	<%
	max_quote_len = 175
	%>
	<%def name="quote_comment(comment, max_len)">
	%	if len(comment) < max_len:
			${comment}
	%	else:
			${comment[:max_len]}...
	%	endif
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
