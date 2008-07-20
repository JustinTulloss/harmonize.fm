<%!
    from masterapp.model import BlogEntry, Spotlight, SpotlightComment, \
                                Recommendation
    from simplejson import dumps
    from datetime import date
%>

<%def name="feed_separator(entry_date)">
    <tr><td colspan="4"><div class="feed-separator">
        % if (date.today() - entry_date).days == 1:
            Yesterday
        % else:
            ${entry_date.strftime('%B %d')}
        % endif
    </div></td></tr>
</%def>

<%def name="render(entries)">

    <%def name="blog_feed(entry)">
		<td class="desc">
			<table><tr><td>
				<img src="/images/post.png" />
			</td><td>
				<div class="title">${entry.author} wrote a new
					<a href="#/player/blog/${entry.id}">post</a>
				</div>
				<div>"${entry.title}"</div>
			</td></tr></table>
        </td>
		<td class="comment">${quote_comment(entry.entry, 60)}</td>
		<td></td>
    </%def>

    <%def name="spotlight_feed(entry)">
		<td class="desc">
			<table><tr><td>
				<img src="/images/spotlight.png" />
			</td><td>
				<div class="title">
				<a href="#/people/profile/${entry.user.id}">
					${entry.user.name}</a>
					added a 
					<a href="#/people/profile/${entry.user.id}">Spotlight</a>
				</div>
			</td></tr>
			<tr><td>
				<a href="#/action/enqueue/${entry.type}/${entry.typeid}&Friend_id=${entry.uid}">
					<img title="Enqueue" src="/images/enqueue.png" />
				</a>
			</td><td>
				<div class="album">${entry.title}</div>
				<div class="artist">by ${entry.author}</div>
			</td></tr></table>
		</td><td class="comment">
			${quote_comment(entry.comment, 175)}
		</td><td class="art">
		${h.p_image_tag(entry.smallart)}</td>
		</td>
    </%def>

    <%def name="comment_feed(entry)">
        <td class="desc">
			<table><tr><td>
				<img src="/images/bubble.png" />
			</td><td>
				<div class="title">
					<a href="#/people/profile/${entry.user.id}">
						${entry.user.name}
					</a>
					<a href="#/people/profile/${entry.spotlight.uid}/spcomments/${entry.spotlight.id}">
						commented
					</a>
					on ${entry.spotlight.title}
				</div>
			</td></tr></table>
		</td>
		<td class="comment">
                ${quote_comment(entry.comment, 75)}
		</td>
		<td></td>
    </%def>

    <%def name="rec_feed(entry)">
		<td class="desc">
			<table><tr><td>
				<img src="/images/recommend.png" />
			</td><td>
				<div class="title">
					<a href="#/people/profile/${entry.recommenderid}">
						${entry.recommender.name}
					</a> 
					recommended you
					% if entry.albumid != None:
						an
					% else:
						a
					% endif
					<a href="#people/profile/${entry.recommendeeid}">
						${entry.type}:
					</a>
				</div>
			</td></tr><tr><td>
				<a href="#/action/enqueue/${entry.type}/${entry.typeid}&Friend_id=${entry.recommenderid}">
					<img title="Enqueue" src="/images/enqueue.png" />
				</a>
			</td><td>
				<div class="album">${entry.title}</div>
				<div class="artist">by ${entry.author}</div>
			</td></tr></table>
		</td><td class="comment">
            % if entry.comment:
                <div class="blog_feed_content">${entry.comment}</div>
            % endif
			</td><td>
		</td>
    </%def>

    <%
    max_quote_len = 175
    %>
    <%def name="quote_comment(comment, max_len)">
	% if comment:
		% if len(comment) < max_len:
			${comment}
		% else:
			${comment[:max_len]}...
		% endif
	% endif
    </%def>

    <div id="news_feed">

        <div id="news-header" class="h-title">music feed</div>
		<table>
    <%
        type_table = {
            BlogEntry : blog_feed,
            Spotlight : spotlight_feed,
            SpotlightComment: comment_feed,
            Recommendation: rec_feed
        }

        last_date = date.today()
    %>
    %   for entry in entries:
            % if hasattr(entry, 'timestamp') and entry.timestamp:
                <% curr_date = entry.timestamp.date() %>
                % if curr_date != last_date:
                    ${feed_separator(curr_date)}
                    <% last_date = curr_date %>
                % endif
            % endif

			<tr>
            ${type_table[type(entry)](entry)}
			</tr>
    %   endfor
	</table>
    </div>
</%def>
