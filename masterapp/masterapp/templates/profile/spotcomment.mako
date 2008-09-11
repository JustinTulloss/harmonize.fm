<%!
from masterapp.model import Session, User
from masterapp.lib.html import linebreaks, urlize
%>

<%def name="render(spotlight)">
    <div class="comments-body" style="display: none;">
        % for spot_comment in spotlight.friend_comments:
            ${render_comment(spot_comment)}
        % endfor

        <div class="profile-sp-comment h-light-form">
		<table><tr><td style="width:100%;">
        <textarea class="spot-comment-textarea"></textarea>
        <div class="profile-right"><button class="send-spot-comment">post</button></div>
		</td><td>
		<div class="profile-albumart fake-albumart"></div>
		</td></tr></table>
        </div>
    </div>
</%def>


<%def name="render_comment(spot_comment)">
    <div class="profile-sp-comment">
    <%
        user = Session.query(User).get(spot_comment.uid)
    %>
    % if c.current_uid == spot_comment.uid:
        You wrote
    % else:
        <a href="#/people/profile/${spot_comment.uid}">
                ${spot_comment.user.get_name()}</a> wrote on 
                <span class="spotlight_timestamp">${spot_comment.timestamp.strftime("%b %d")}</span>:
    % endif
        <div>
            % if user.swatch:
                <span class="profile-sp-comment-pic">
                    <img src=${user.swatch} />
                </span>
            % endif
            <div class="profile-sp-comment-text">
                ${linebreaks(urlize(spot_comment.comment))}
            </div>
        </div>
    </div>
</%def>
