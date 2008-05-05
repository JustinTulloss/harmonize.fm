<div class = 'albumdetails'>
    <table class="albumsongtable">
    <% numsongs = len(c.album.songs)+1%>
    % for col in xrange(0,numsongs/3):
        <tr class="albumsongrow">
            % if c.album.smallart != None and col == 0:
                <td class="albumart" rowspan="${numsongs}">
                    <img src='${c.album.smallart}' />
                </td>
            % endif
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
    </table>
</div>
