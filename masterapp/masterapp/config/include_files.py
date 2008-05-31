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
        'menu',
        'button',
        'box',
        'form',
        'slider'
    ],
    templated_stylesheets = [
        'player_css/player_css.mako',
        'player_css/queue_css.mako',
        'player_css/album_details.mako',
        'player_css/topbar.mako',
        'player_css/statusbar.mako',
        'profile/profile.css.mako'
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
        'player/extbrowser.js',
        'player/bcmgr.js',
        'player/settingspanel.js',
        'player/queueui.js',
        'player/playqueue.js',
        'player/player.js',
        #'player/auth.js',
        'player/metatypeinfo.js',
        'player/columns.js',
        'player/init.js',
        'player/feedback.js',
		'player/spotlight.js',
		'player/urlmanager.js'
    ]
)

compressed_player_files = IncludeFiles(
    stylesheets = ['compressed/player'],
    templated_stylesheets = [
        'player_css/player_css.mako',
        'player_css/queue_css.mako',
        'player_css/album_details.mako',
        'player_css/topbar.mako',
        'player_css/statusbar.mako'
    ],
    javascripts = ['compressed/player.js']
)
