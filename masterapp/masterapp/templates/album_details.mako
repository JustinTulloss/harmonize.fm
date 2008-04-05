<div class = 'albumdetails'>
    % if c.album.smallart != None:
        <div class='albumart'>
            <img src='${c.album.smallart}' />
        </div>
    % endif
    <div class = 'album'>${c.album.album}</div>
    <div class = 'artist'>${c.album.artist}</div>
    <div class = 'year'>${c.album.year}</div>
</div>
