class IncludeFiles(object):
    def __init__(self, 
            stylesheets = [], templated_stylesheets=[], javascripts = []):
        self.stylesheets = stylesheets
        self.templated_stylesheets = templated_stylesheets
        self.javascripts = javascripts

player_files = IncludeFiles(
    stylesheets = [
        'core',
        'ext-ux-slidezone',
        'layout',
        'borders',
        'resizable',
        'grid',
        'tree',
        'dd',
        'borders',
        'panel',
        'toolbar',
        'box',
        'slider'
    ],
    templated_stylesheets = [
        'window.css.mako',
        'form.css.mako',
        'button.css.mako',
        'combo.css.mako',
        'menu.mako.css',
        'harmonize.mako.css',
        'player_css/player_css.mako',
        'player_css/queue_css.mako',
        'player_css/album_details.mako',
        'player_css/topbar.mako',
        'player_css/statusbar.mako',
        'profile/profile.css.mako',
		'player_css/dialog.mako.css'
    ],
    javascripts = [
        'lib/ext-2.1/adapter/ext/ext-base.js',
        'lib/ext-2.1/ext-all-debug.js',
        'lib/ext-2.1/source/widgets/ux/SlideZone.js',
        'lib/ext-2.1/source/widgets/ux/RowExpander.js',
        'lib/soundmanager2.js',
        'lib/helpers.js',
        'player/errmgr.js',
        'player/viewmgr.js',
        'player/friendrec.js',
        'player/extbrowser.js',
        'player/bcmgr.js',
        'player/settingspanel.js',
        'player/queueui.js',
        'player/playqueue.js',
        'player/player.js',
        'player/metatypeinfo.js',
        'player/init.js',
        'player/feedback.js',
		'player/spotlight.js',
		'player/urlmanager.js',
        'player/columns.js',
        'player/profile.js',
        'player/friendradio.js',
        'player/playlist.js',
        'player/invite.js',
    ]
)

compressed_player_files = IncludeFiles(
    stylesheets = ['compressed/player'],
    templated_stylesheets = player_files.templated_stylesheets,
    javascripts = ['compressed/player.js']
)
