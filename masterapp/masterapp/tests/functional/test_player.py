from masterapp.tests import *
import re
from mock import Mock
from pylons import config
#from masterapp import model

class TestPlayerController(TestModel):
    def test_index(self):
        """
        Testing /player
        """
        response = self.app.get(
            url_for(controller='player'), headers = self.win_ff2_headers)
        # Test response...
        assert response.c.profile != None
        assert 'player | harmonize.fm' in response

        response = self.app.get(
            url_for(controller='player'), headers = self.win_ie6_headers)
        response = response.follow()
        assert 'Internet Explorer 6' in response.body

    def test_new_user(self):
        """
        Testing /player without a user
        """
        # Test creating a user
        model.Session.delete(self.user)
        model.Session.commit()
        response = self.app.get(
            url_for(controller='player'), headers=self.win_ff2_headers)
        assert 'player | harmonize.fm' in response

    def test_get_song_url(self):
        """
        Testing /player/songurl/<songid>
        """

        self.user.update_profile = Mock()

        # Test 404 for a non-existent song
        response = self.app.get(url_for(
            controller='player',
            action = 'songurl',
            id = 7
        ), status=404)


        # Test for a song I do own
        ns = generate_fake_song(model.Session.query(model.User).first())
        response = self.app.get(url_for(
            controller='player',
            action = 'songurl',
            id = ns.id
        ))

        # Test for a song i own and set now playing
        ns = generate_fake_song(model.Session.query(model.User).one())
        ns2 = generate_fake_song(model.Session.query(model.User).one())
        response = self.app.get(url_for(
            controller = 'player',
            action = 'songurl',
            id = ns.id
        ), params = { 'pid': ns2.id})

        model.Session.add(self.user) #rebind user
        model.Session.add(ns2)
        assert self.user.nowplaying.id == ns2.id, \
            'Did not set nowplaying correctly'
        assert self.user.update_profile.called, \
            'Did not update facebook profile'

        assert re.search(ns.sha, response.body),\
            'Did not return the sha in the URL'
        
        # Test for a song none of my friends own
        anewuser = generate_fake_user()
        anewsong = generate_fake_song(anewuser)

        response = self.app.get(url_for(
            controller='player',
            action = 'songurl',
            id = anewsong.id
        ), params={'friend': anewuser.id}, status=401)

    def test_album_details(self):
        """
        Testing /player/album_details
        """

        # Test an illegit request
        response = self.app.get(url_for(
            controller = 'player',
            action = 'album_details',
        ), params={'album': 1}, status=404)
        
        # Fake some data
        mysong = generate_fake_song(self.user)
        friend = generate_fake_user(config['pyfacebook.fbfriendid'])
        friendsong = generate_fake_song(friend)

        # Test details for one of my albums
        response = self.app.get(url_for(
            controller = 'player',
            action = 'album_details',
        ), params={'album': mysong.albumid})
        assert mysong.title in response, \
            "Did not return the details on my own album"

        # Test details for one of my friends' albums
        response = self.app.get(url_for(
            controller = 'player',
            action = 'album_details',
        ), params={'album': friendsong.albumid, 'friend': friend.id})
        assert friendsong.title in response, \
            "Did not return the details on my friend's album"

    def test_username(self):
        """
        Testing /player/username
        """
        response = self.app.get(url_for(
            controller = 'player',
            action = 'username',
        ))
        assert response.body == self.user.name, \
            "Did not return correct name"

    def test_feedback(self):
        """
        Testing /player/feedback
        """

        # Illegit request
        response = self.app.get(url_for(
            controller = 'player',
            action = 'feedback'
        ))
        assert response.body =='0',\
            "feedback w/out params request went unnoticed"

        response = self.app.get(url_for(
            controller = 'player',
            action = 'feedback'
        ), params={'email': '', 'feedback': ''})
        assert response.body == '0', "Empty feedback went unnoticed"

        response = self.app.get(url_for(
            controller = 'player',
            action = 'feedback'
        ), params={'email': '', 'feedback': 'Something to say'})
        assert response.body == '1', "Legit feedback didn't get legit response"

        # Since most of the actual mail sending stuff happens in another thread,
        # this is a bit difficult to test. At least we know we're not getting
        # 500 errors.

        response = self.app.get(url_for(
            controller = 'player',
            action = 'feedback'
        ), params={'email': 'justin@harmonize.fm', 'feedback': 'Something to say'})
        assert response.body == '1', "Legit email didn't get legit response"

    def test_blog(self):
        """
        Testing /player/blog
        """

        response = self.app.get(url_for(
            controller = 'player',
            action = 'blog'
        ))
        assert 'News' in response.body, "Blog did not return"

    def test_home(self):
        """
        Testing /player/home
        """
        response = self.app.get(url_for(
            controller = 'player',
            action = 'home'
        ), headers = self.win_ff2_headers)
        assert 'Harmonizer Setup.exe' in response.body,\
            "Windows link to harmonizer not on home page"

        response = self.app.get(url_for(
            controller = 'player',
            action = 'home'
        ), headers = self.mac_safari3_headers)
        assert 'Harmonizer.dmg' in response.body,\
            "Mac link to harmonizer not on home page"


        response = self.app.get(url_for(
            controller = 'player',
            action = 'home'
        ), headers = self.linux_ff3_headers)
        assert '/harmonizer-not-supported' in response.body,\
            "Linux not supported link not on home page"

    def test_set_volume(self):
        """
        Testing /player/set_volume
        """
        response = self.app.get(url_for(
            controller = 'player',
            action = 'set_volume',
            id = 43
        ))

        assert self.user.lastvolume == 43, 'Volume was not set'
