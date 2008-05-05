<div class = 'albumdetails'>
    % if c.album.smallart != None:
        <span class='albumart'>
            <img src='${c.album.smallart}' />
        </span>
    % endif
    <span>
    <% numsongs = len(c.album.songs) %>
    % for col in xrange(0,3):
        <span class=songcol>
            % for cell in xrange(col*(numsongs-1)/3, (col+1)*(numsongs-1)/3):
                <div class="albumsong">
                    <% song = c.album.songs[cell] %>
                    <span>${song.tracknumber}</span>
                    <span>${song.title}</span>
                </div>
            %endfor
        </span>
    % endfor
    </span>
</div>
