from masterapp.tests import *
from masterapp.lib.fakefacebook import friends, friends_info, friend_info

class TestPeopleController(TestModel):

    def test_profile(self):
        """
        Testing /people/profile/<userid>
        """
        response = self.app.get(url_for(
            controller = 'people',
            action = 'profile',
            id = None
        ), headers=self.mac_safari3_headers)


        assert self.user.name in response.body,\
            "Did not give user own profile without a userid"

        friend = generate_fake_user(friends[0])
        response = self.app.get(url_for(
            controller = 'people',
            action = 'profile',
            id = friend.id
        ), headers=self.win_ff2_headers)

        assert friend_info[0]['name'] in response.body,\
            "Did load friend profile correctly"

        # Test non-existent profile
        response = self.app.get(url_for(
            controller = 'people',
            action = 'profile',
            id = 100
        ), headers=self.linux_ff3_headers, status=404)

    def test_invite(self):
        """
        Testing /people/invite/<fbid>
        """
        response = self.app.get(url_for(
            controller = 'people',
            action = 'invite',
            id = None
        ), status = 400)

        response = self.app.get(url_for(
            controller = 'people',
            action = 'invite',
            id = friends[0]
        )) 
        assert response.body == '1',\
            "No positive response"

    def test_add_spotcomment(self):
        """
        Testing /people/add_spotcomment/<spotlightid>
        """
        response = self.app.get(url_for(
            controller = 'people',
            action = 'add_spotcomment',
            id = None
        ), status = 400)

        # Create a spotlight
        song = generate_fake_song(self.user)
        response = self.app.get(url_for(
            controller = 'spotlight',
            action = 'album',
            id = song.albumid
        ), params = {'comment': 'spotted^light'})
        spot_id = int(response.body)

        # Comment on that spotlight
        response = self.app.get(url_for(
            controller = 'people',
            action = 'add_spotcomment',
            id = spot_id
        ), params = {'comment': 'walking on sunshine'})
        comment_id = int(response.body)
        comment = model.Session.query(model.SpotlightComment).get(comment_id)
        assert comment, "comment not created"
        assert comment.spotlightid == spot_id, \
            "comment not associated with spotlight"

