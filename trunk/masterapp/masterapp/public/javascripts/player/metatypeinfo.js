/* Justin Tulloss - 03/03/2008
 *
 * This file describes all the information about our different metadata types.
 * Right now I think I'm just going to keep it as a global since there's not
 * really a good way to import things in javascript. Instead, everything will
 * just assume that it exists. Let's hope I don't hate myself for that later.
 */

var typeinfo = {
    home:{
        display:'Home'
    },
    artist:{
        next:'album', 
        display:'Artists'
    }, 
    album:{
        next:'song', 
        qry:'albumid', 
        display:'Albums'
    }, 
    playlist:{
        next:'playlistsong', 
        qry:'playlistid', 
        display:'Playlists'
    },
    song:{
        next:'play', 
        display:'Songs'
    },
    playlistsong:{
        next:'play', 
        display:'Songs'
    },
    friend:{
        next:'artist', 
        qry:'fbid', 
        display:'Friends'
    }
};

var fields = ['type', 'title', 'artist', 'album', 'year', 'genre', 
                  'tracknumber', 'totaltracks', 'totalalbums','recs', 
                  'albumlength', 'artistlength', 'numartists','numalbums',
                  'likesartists', 'exartists', 'numtracks', 'name', 'friend',
                  'songid', 'albumid', 'id', 'fbid', 'length', 'playlistid'];

