<div class = 'albumdetails'>
    <table class="albumsongtable">
    % if c.album.smallart != None:
        <tr>
        <td class="albumart">
            <img class="albumart" src='${c.album.smallart}' />
        </td>
        <td class="albumsong">
        <table class="albumsongcell">
    % endif
    <% numsongs = len(c.album.songs)+1%>
    % for col in xrange(0,numsongs/3):
        <tr class="albumsongrow">
            % for cell in xrange(0, 3):
                <td class="albumsong">
                    <% 
                        try:
                            song = c.album.songs[cell*numsongs/3 +col]
                        except:
                            break
                    %>
                    <span>${song.tracknumber}.</span>
                    <span>${song.title}</span>
                </td>
            %endfor
        </tr>
    % endfor
    % if c.album.smallart != None:
        </table>
        </td>
        </tr>
    % endif
    </table>
</div>
