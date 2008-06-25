<%namespace name="feed" file="feed.mako" />

<%def name="render(entries)">
        <div id="home">
            <div id="no_music">
            <% 
            href = None
            if c.num_songs == 0:
                if c.platform == 'windows':
                    href = '/uploaders/setup.exe'
                elif c.platform == 'mac':
                    href = '/uploaders/Harmonize.dmg'
                endif
            endif
            %>
            % if c.num_songs==0:
                <h2>You haven't added any music yet.  Install the <a href="${href}">uploader</a> to get started.</h2>
            % endif
            </div>                  
            <div id="home-bg">  
                <div id="home-sidebar">         
                    <div id="home-sidebar-header" class="h-subtitle">Links</div>
                    % if href:
                        <div><a href="${href}">Download the uploader</a></div>
                    % endif
                    <div><a href="#/player/blog">News</a></div>
                    % if not c.user.hasfbapp:
                        <div>
                            <a href="${c.fbapp_href}">Add the facebook app</a>
                        </div>
                    % endif
                </div>
            </div>
            ${feed.render(entries)}
            <!--div id="mainlogo"><img src="/images/bigharmonized2.png" /></div-->
        </div>
</%def>

%   if hasattr(c, 'main') and c.main:
    ${render(c.entries)}
%   endif
