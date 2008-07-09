from mockfacebook import MockFacebook
from facebook.wsgi import FacebookWSGIMiddleware

class Fakethebook(MockFacebook):
    _uid = 1909354
    _session = 'hit me baby one more time'

    # Preset return values
    configured_friends =  [1908861, 1932106]
    configured_info = [
        {'name': 'Brian Smith', 'uid': 1908861},
        {'name': 'David Paola', 'uid': 1932106}
    ]
    configured_user_info = [{
        'name': 'Justin Tulloss',
        'uid': 1909354,
        'first_name': 'Justin',
        'has_added_app': True,
        'pic_big': 'bigurl',
        'pic_square': 'squareurl',
        'pic': 'picurl',
        'sex': 'yes',
        'music': 'Britney Spears and Bach'
    }]

def setup_fake_facebook(app, app_conf):
    app = FacebookWSGIMiddleware(app, app_conf, facebook_class=Fakethebook)
    return app

