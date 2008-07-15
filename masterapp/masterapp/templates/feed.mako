<%!
    from masterapp.model import BlogEntry, Spotlight, SpotlightComment, \
                                Recommendation
    from simplejson import dumps
    from datetime import date
%>

<%def name="feed_separator(entry_date)">
    <div class="feed-separator">
        % if (date.today() - entry_date).days == 1:
            Yesterday
        % else:
            ${entry_date.strftime('%B %d')}
        % endif
    </div>
</%def>

<%def name="render(entries)">

    <%def name="blog_feed(entry)">
        <div class="feed_content">
            <h2><a href="#/player/blog/${entry.id}">
                ${entry.author} wrote a post titled "${entry.title}"</a></h2>
            <div class="blog_feed_comment">
                ${quote_comment(entry.entry, 60)}</div>
        </div>
    </%def>

    <%def name="spotlight_feed(entry)">
        % if entry.album != None:
            <img src="/images/enqueue.png" onclick="enqueue_album(${entry.album.id}, ${entry.uid});" />
            <div class="feed_content">
                <h2><a href="#/people/profile/${entry.user.id}">
                    ${entry.user.firstname} 
                    added a Spotlight on ${entry.album.title}</a></h2>
                <table class="spotlight_feed_info"><tr>
                    <!--td><img src="/images/enqueue.png" /></td-->
                    <td>${h.p_image_tag(entry.album.smallart)}</td>
                    <td class="spotlight_feed_comment">
                    ${quote_comment(entry.comment, 175)}
                    </td>
                </tr></table>
            </div>
        % elif entry.playlist != None:
            <img src="/images/enqueue.png" onclick="enqueue_playlist(${entry.playlist.id}, ${entry.uid});" />
            <div class="feed_content">
                <h2><a href="#/people/profile/${entry.user.id}">
                    ${entry.user.get_firstname()} 
                    added a Spotlight on a playlist: ${entry.playlist.name}</a></h2>
                <table class="spotlight_feed_info"><tr>
                    <td class="spotlight_feed_comment">
                    ${quote_comment(entry.comment, 175)}
                    </td>
                </tr></table>
            </div>
        % endif
    </%def>

    <%def name="comment_feed(entry)">
        <div class="feed_content">
            <h2>
            <a href="#/people/profile/${entry.spotlight.uid}/spcomments/${entry.spotlight.id}">
                ${entry.user.get_firstname()} commented on 
            % if entry.spotlight.uid == c.user.id:
                your
            % elif entry.uid == entry.spotlight.uid:
                % if entry.spotlight.user.sex == 'female':
                    her
                % else:
                    his
                % endif
            % else:
                ${entry.spotlight.user.get_firstname()}'s 
            % endif
                % if entry.spotlight.album:
                    Spotlight of ${entry.spotlight.album.title}
                % elif entry.spotlight.playlist:
                    Spotlight of ${entry.spotlight.playlist.name}
                % endif
            </a></h2>
            <div class="blog_feed_comment">
                ${quote_comment(entry.comment, 75)}
            </div>
        </div>
    </%def>

    <%def name="make_rec_enqueue(type, id)">
        <a href="#/action/enqueue/${type}/${id}">
            <img src="/images/enqueue.png" />
        </a>
    </%def>

    <%def name="rec_feed(entry)">
        % if entry.albumid != None:
            ${make_rec_enqueue('album', entry.albumid)}
        % elif entry.songid != None:
            ${make_rec_enqueue('song', entry.songid)}
        % else:
            ${make_rec_enqueue('playlist', entry.playlistid)}
        % endif
        <div class="feed_content">
            <h2>
            <a href="#/people/profile/${entry.recommendeeid}">
                ${entry.recommender.name} recommended the
                % if entry.albumid != None:
                    album ${entry.album.title}
                % elif entry.songid != None:
                    song ${entry.song.title}
                % else:
                    playlist ${entry.playlist.name}
                % endif
                to you
            </a></h2>
            % if entry.comment:
                <div class="blog_feed_content">${entry.comment}</div>
            % endif
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

        <div><div id="news-header" class="h-title">music feed</div></div>
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

            <div class="feed_entry">
            ${type_table[type(entry)](entry)}
            </div>
    %   endfor
    </div>
</%def>
