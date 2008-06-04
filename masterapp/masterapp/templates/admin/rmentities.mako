<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Clean Database</title>
</%def>

<%def name="body()">
    ${h.rails.form('rmalbums', method='GET')}
    <h4>Albums</h4>
    <table>
        <tr>
            <th>RM</th>
            <th>Album</th>
            <th>Artist</th>
            <th>MusicBrainz ID</th>
        </tr>
        % for album in c.albums:
            ${makealbumrow(album)}
        % endfor
    </table>
    ${h.rails.submit(
        value='Remove Albums', 
        name='commitalbums', 
        confirm='Are you sure?'
    )}
    ${h.rails.end_form()}
    ${h.rails.form('rmsongs', method='GET')}
    <h4>Songs</h4>
    <table>
        <tr>
            <th>RM</th>
            <th>Track</th>
            <th>Title</th>
            <th>Album</th>
            <th>Artist</th>
        </tr>
        % for song in c.songs:
            ${makesongrow(song)}
        % endfor
    </table>
    ${h.rails.submit(
        value='Remove Songs', 
        name='commitsongs', 
        confirm='Are you sure?'
    )}
    ${h.rails.end_form()}
</%def>

<%def name="makealbumrow(album)">
    <tr>
        <td>${h.rails.check_box(album.id)}</td>
        <td>${album.title}</td>
        <td>${album.artist.name}</td>
        <td>${album.mbid}</td>
    </tr>
</%def>

<%def name="makesongrow(song)">
    <tr>
        <td>${h.rails.check_box(song.id)}</td>
        <td>${song.tracknumber}</td>
        <td>${song.title}</td>
        <td>${song.album.title}</td>
        <td>${song.artist.name}</td>
    </tr>
</%def>
