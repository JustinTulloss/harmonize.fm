<%def name="render(spotlight)">
    <div class="comments-body" style="display: none;">
        Comments:&nbsp;
        <a href="${c.current_url}" class="profile-sp-comment">hide</a>
        % for spot_comment in spotlight.friend_comments:
            ${render_comment(spot_comment)}
        % endfor

        <div class="profile-sp-comment">
        <textarea class="spot-comment-textarea"></textarea>
        <br />
        <button class="send-spot-comment">post</button>
        </div>
    </div>
</%def>


<%def name="render_comment(spot_comment)">
    <div class="profile-sp-comment">
    % if c.user.id == spot_comment.uid:
        You wrote:
    % else:
        <a href="#/people/profile/${spot_comment.uid}">
                ${spot_comment.user.get_name()}</a> wrote:
    % endif
        <div>${spot_comment.comment}</div>
    </div>
</%def>
