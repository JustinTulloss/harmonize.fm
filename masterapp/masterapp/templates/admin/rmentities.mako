<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Clean Database</title>
</%def>

<%def name="body()">
    ${h.html.tags.form('rmalbums', method='GET')}
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
    ${h.html.tags.submit(
        value='Remove Albums', 
        name='commitalbums', 
        confirm='Are you sure?'
    )}
    ${h.html.tags.end_form()}
    ${h.html.tags.form('rmsongs', method='GET')}
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
    ${h.html.tags.submit(
        value='Remove Songs', 
        name='commitsongs', 
        confirm='Are you sure?'
    )}
    ${h.html.tags.end_form()}
</%def>

<%def name="makealbumrow(album)">
    <tr>
        <td>${h.html.tags.checkbox(album.id)}</td>
        <td>${album.title}</td>
        <td>${album.artist.name}</td>
        <td>${album.mbid}</td>
    </tr>
</%def>

<%def name="makesongrow(song)">
    <tr>
        <td>${h.html.tags.checkbox(song.id)}</td>
        <td>${song.tracknumber}</td>
        <td>${song.title}</td>
        <td>${song.album.title}</td>
        <td>${song.artist.name}</td>
    </tr>
</%def>
