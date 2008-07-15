/* Define all our columns. This will also be read by the server to determine
 * what to send to the client
 */

var defaultWidths = {
    'Album_title': 225,
    'Artist_name': 175,
    'Song_title': 400
};

/* Column Renderers */
/* Action Templates */
var every_action =  {
    enqueue_row:{
        view:'<a href="#/action/enqueue_row"><img title="Enqueue" src="/images/enqueue.png" /></a>',
        action: function(record) {playlistmgr.enqueue([record]);}
    },
    friendrec: { 
        view: '<a href="#/action/friendrec"><img title="Recommend to a friend" src="/images/recommend.png" /></a>',
        action: friend_recommend
    },
    spotlight: {
        view: '<a href="#/action/spotlight"><img title="Spotlight" src="/images/spotlight.png" /></a>',
        action: function(record) {
            //we need to check and make sure this spotlight doesn't already exist
            var album_id = record.get('Album_id');
            var playlist_id = record.get('Playlist_id');
            if (album_id) {
                Ext.Ajax.request({
                    url: '/spotlight/find_by_album/' + album_id,
                    success: function(response, options) {
                        if (response.responseText == "1") {
                            show_status_msg("You already have a spotlight for this album.");
                        } else {
                            show_spotlight(record, "add");
                        }                
                    },
                    failure: function(response, options) {
                        show_spotlight(record, "add");                
                    }            
                });
            } else if (playlist_id) {
                Ext.Ajax.request({
                    url: '/spotlight/find_by_playlist/'+playlist_id,
                    success: function(response, options) {
                        if (response.responseText == "1") {
                            show_status_msg("You already have a spotlight for this playlist.");
                        } else {
                            show_spotlight(record, "add_playlist");
                        }
                    },
                    failure: function(response, options) {
                        show_spotlight(record, "add_playlist");
                    }                
                });
            }
        }
    },
    playnow: {
        view: '<a href="#/action/playnow"><img title="Play now" src="/images/control_play_blue.png" /></a>',
        action: function(record) {playqueue.insert([record], true);}
    },
    delrow: {
        view: '<a href="#/action/delrow"><img title="Remove from library" src="/images/cross.png" /></a>',
        action: function(record) {
            if(typeinfo[record.get('type')].remove)
                typeinfo[record.get('type')].remove(record);
            else {
                var type = record.get('type');
                var title = record.get(typeinfo[type].lblindex)
                urlm.register_action('cancel_remove', function (){
                    hide_dialog();
                });
                urlm.register_action('really_remove', function (){
                    var index = record.get(typeinfo[type].qryindex);
                    hide_dialog();
                    Ext.Ajax.request({
                        url: ['/metadata', 'remove', record.get('type'), index].join('/'),
                        success: function() {
                            show_status_msg('Successfully removed '+ title);
                            urlm.unregister_action('cancel_remove');
                            urlm.unregister_action('really_remove');
                            Hfm.breadcrumb.reload();
                        }
                    });
                });
                show_dialog(['<h1> Remove from Library</h1><h2>',title,'</h2>',
                    '<div class="h-dlg-buttons">',
                        '<a href="#/action/cancel_remove" class="a-button">cancel</a>',
                        '<a href="#/action/really_remove" class="a-button">remove</a>',
                    '</div>'].join('')
                );
            }
        }
    }
};

for (action_key in every_action) {
    (function(action_key) {
        urlm.register_action(action_key, function(match, target){
            var crumb = Hfm.breadcrumb.current_view()
            var record = crumb.panel.find_record(new Ext.Element(target));
            every_action[action_key].action(record);
        });
    })(action_key);
}

var render = {

    actionColumn: function (value, p, record)
    {
        var type = record.get('type');
        var allactions = typeinfo[type].actions;
        var ownactions = typeinfo[type].ownactions;
        var html = ['<span class="grid-actions">'];
        
        if (allactions) {
            for (var i=0; i<allactions.length; i++)
                html.push(every_action[allactions[i]].view);
        }

        if (own_record(record)) {
            if (ownactions) {
                for (var i=0; i<ownactions.length; i++)
                    html.push(every_action[ownactions[i]].view);
            }
        }

        html.push('</span>');
        return html.join('');
    },

    starColumn: function (value, p, record)
    {
        //figure out opacity from record.recs (or something like that)
        recs = record.get('recs')
        opacity = 0
        if (recs != 0)
            opacity = record.get('recs')/record.store.sum('recs');  
        return '<center><img style="opacity:'+opacity+'" src="/images/star.png" /></center>';
    },

    lengthColumn: function (value, p, record)
    {
        return format_time(value)
    },


    availColumn: function (value, p, record)
    {
        ret = value;
        total = record.get('Album_totaltracks');
        if (total)
            ret = value + ' of ' + total;

        return ret
    }
}

var BrowserColumns = {
    'Song_tracknumber': {
        id: 'tracknumber', 
        header: "Track",
        width: 60,
        fixed: true,
        renderer: render.availColumn,
        dataIndex: 'Song_tracknumber'
    },
    'Song_title': {
        id: 'title', 
        width: defaultWidths.Song_title,
        header: "Title",
        dataIndex: 'Song_title'
    }, 
    'Song_length': {
        id:'length',
        header: "Length",
        renderer: render.lengthColumn,
        width: 60,
        fixed: true,
        dataIndex: 'Song_length'
    },
    'Album_title': {
        id: 'album',
        header: 'Album',
        sortable: true,
        width: defaultWidths.Album_title,
        dataIndex: 'Album_title'
    },
    'Album_year': {
        id: 'year',
        header: "Year",
        width: 50,
        fixed: true,
        dataIndex: 'Album_year'
    },
    'Album_length': {
        id:'album_playtime',
        header: "Length",
        renderer: render.lengthColumn,
        fixed: true,
        width: 65,
        dataIndex: 'Album_length'
    },
    'Album_availsongs': {
        id:'num_tracks',
        header: "Tracks",
        width: 65,
        fixed: true,
        dataIndex: 'Album_havesongs',
        renderer: render.availColumn
    },
    'Artist_name': {
        id: 'artist',
        header: 'Artist',
        sortable: true,
        width: defaultWidths.Artist_name,
        dataIndex: 'Artist_name'
    },
    'Artist_numalbums': {
        id:'num_albums',
        width: 60,
        fixed: true,
        header: "Albums",
        css:'text-align: center;',
        dataIndex: 'Artist_numalbums'
    },
    'Artist_availsongs': {
        id:'num_tracks',
        header: "Songs",
        width: 50,
        fixed: true,
        css:'text-align: center;',
        dataIndex: 'Artist_availsongs',
        renderer: render.availColumn
    },
    'Artist_length': {
        id:'artistplaytime',
        header: "Total Time",
        dataIndex: 'Artist_length'
    },
    'Playlist_name': {
        id:'name',
        header: "Name",
        dataIndex: 'Playlist_name'
    },
    'Playlist_songcount': {
        id: 'songcount',
        header: 'Tracks',
        dataIndex: 'Playlist_songcount',
		width: 65,
		fixed: true
    },
    'Playlist_length': {
        id:'length',
        header: 'Length',
        dataIndex: 'Playlist_length',
		width: 65,
        renderer: render.lengthColumn,
		fixed: true
    },
    'Friend_name': {
        id:'friend',
        width: 50,
        header: "Friend",
        dataIndex: 'Friend_name'
    },
    'Friend_albumcount': {
        id:'numalbums',
        width: 60,
        fixed: true,
        header: "Albums",
        dataIndex: 'Friend_albumcount'
    },
    'Friend_songcount': {
        id:'numsongs',
        width: 60,
        fixed: true,
        header: "Songs",
        dataIndex: 'Friend_songcount'
    },
    'Friend_tastes': {
        id:'likesartists',
        header: "Tastes",
        dataIndex: 'Friend_tastes'
    },
    'actions': {  
        id: 'add',
        header: 'Actions',
        css:'text-align: center;',
        renderer: render.actionColumn,
        fixed: true,
        width: 100,
        sortable: false
    },
    'expander': new Ext.grid.RowExpander()
};

var ColConfig = {
    song: [
        BrowserColumns['actions'], 
        BrowserColumns['Song_tracknumber'], 
        BrowserColumns['Song_title'], 
        BrowserColumns['Album_title'], 
        BrowserColumns['Artist_name'], 
        BrowserColumns['Song_length']
    ],
    album: [
        BrowserColumns['expander'],
        BrowserColumns['actions'], 
        BrowserColumns['Album_title'], 
        BrowserColumns['Artist_name'], 
        BrowserColumns['Album_availsongs'], 
        BrowserColumns['Album_length'],
        BrowserColumns['Album_year']
    ],
    artist: [
        BrowserColumns['actions'], 
        BrowserColumns['Artist_name'],
        BrowserColumns['Artist_numalbums'],
        BrowserColumns['Artist_availsongs']
    ],
    playlist: [
		BrowserColumns['actions'],
		BrowserColumns['Playlist_name'],
		BrowserColumns['Playlist_songcount'],
		BrowserColumns['Playlist_length']],
    friend: [
        BrowserColumns['Friend_name'],
        BrowserColumns['Friend_songcount'],
        BrowserColumns['Friend_albumcount'],
        BrowserColumns['Friend_tastes']
    ]
};

