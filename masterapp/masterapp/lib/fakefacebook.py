from mockfacebook import MockFacebook
from facebook.wsgi import FacebookWSGIMiddleware

user_info = [{
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

friend_info = [{
    'name': 'Brian',
    'uid': 1908861,
    'first_name': 'Brian',
    'has_added_app': True,
    'pic_big': 'bigurl',
    'pic_square': 'squareurl',
    'pic': 'picurl',
    'sex': 'yes',
    'music': 'Really lame stuff. All the time.... no, no, like realllly lame.'
}]

friends = [1908861, 1932106]
morefriends = {1909354: friends,
    1908861: [1909354, 1932106]}
friends_info = [
    {'name': 'Brian Smith', 'uid': 1908861},
    {'name': 'David Paola', 'uid': 1932106}
]
class Fakethebook(MockFacebook):
    def __init__(self, *args, **kwargs):
        # Preset return values
        self.configured_friends = morefriends
        self.configured_info = friends_info
        self.configured_user_info = user_info
        self.configured_friend_info = friend_info

        self._uid = 1909354
        self._session = 'hit me baby one more time'


        super(Fakethebook, self).__init__(*args, **kwargs)

def setup_fake_facebook(app, app_conf):
    app = FacebookWSGIMiddleware(app, app_conf, facebook_class=Fakethebook)
    return app

