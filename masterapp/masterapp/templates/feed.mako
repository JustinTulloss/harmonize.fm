<%!
    from masterapp.model import BlogEntry, Spotlight, SpotlightComment
    from simplejson import dumps
%>

<%def name="render(entries)">

    <%def name="blog_feed(entry)">
        <div class="feed_content">
            <h4><a href="#/player/blog/${entry.id}">
                ${entry.author} wrote a post titled "${entry.title}"</a></h4>
            <div class="blog_feed_comment">
                ${quote_comment(entry.entry, 60)}</div>
        </div>
    </%def>

    <%def name="spotlight_feed(entry)">

        <img src="/images/enqueue.png" onclick="enqueue_album(${entry.album.id}, ${entry.uid});" />
        <div class="feed_content">
            <h4><a href="#/people/profile/${entry.user.id}">
                ${entry.user.get_firstname()} 
                added a Spotlight on ${entry.album.title}</a></h4>
            <table class="spotlight_feed_info"><tr>
                <!--td><img src="/images/enqueue.png" /></td-->
                <td><img src="${entry.album.smallart}" /></td>
                <td class="spotlight_feed_comment">
                ${quote_comment(entry.comment, 175)}
                </td>
            </tr></table>
        </div>
    </%def>

    <%def name="comment_feed(entry)">
        <div class="feed_content">
            <h4>
            <a href="#/people/profile/${entry.spotlight.uid}/spcomments/${entry.spotlight.id}">
                ${entry.user.get_firstname()} commented on 
            % if entry.uid == c.user.id:
                your
            % elif entry.uid == entry.spotlight.uid:
                % if c.user.sex == 'female':
                    her
                % else:
                    his
                % endif
            % else:
                ${entry.spotlight.user.get_firstname()}'s 
            % endif
                Spotlight of ${entry.spotlight.album.title}
            </a></h4>
            <div class="blog_feed_comment">
                ${quote_comment(entry.comment, 75)}
            </div>
        </div>
    </%def>

    <%
    max_quote_len = 175
    %>
    <%def name="quote_comment(comment, max_len)">
    %   if len(comment) < max_len:
            ${comment}
    %   else:
            ${comment[:max_len]}...
    %   endif
    </%def>

    <div id="news_feed">
        <div><h1 id="news-header">Music Feed</h1></div>
    <%
        type_table = {
            BlogEntry : blog_feed,
            Spotlight : spotlight_feed,
            SpotlightComment: comment_feed
        }
    %>
    %   for entry in entries:
            <div class="feed_entry">
            ${type_table[type(entry)](entry)}
            </div>
    %   endfor
    </div>
</%def>
