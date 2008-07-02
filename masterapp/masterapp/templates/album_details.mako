<%! import math %>
<div class = 'albumdetails'>
    <table class="albumsongtable">
    % if c.album.Album_smallart != None:
        <tr>
        <td class="albumart">
            <img class="albumart" src='${c.album.Album_smallart}' />
        </td>
        <td class="albumsong">
        <table class="albumsongcell">
    % endif
    <% 
        numsongs = len(c.songs)+1
        numrows = int(math.ceil(numsongs/3.0))
    %>
    % for col in xrange(0,numrows):
        <tr class="albumsongrow">
            % for cell in xrange(0, 3):
                <td class="albumsong">
                    <% 
                        try:
                            song = c.songs[cell*numrows +col]
                        except:
                            break
                    %>
                    <span>${song.Song_tracknumber}.</span>
                    <span>${song.Song_title}</span>
                </td>
            %endfor
        </tr>
    % endfor
    % if c.album.Album_smallart != None:
        </table>
        </td>
        </tr>
    % endif
    </table>
</div>
