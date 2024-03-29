from django.shortcuts import reverse
from django.test import TestCase

from ..models import FriendsModel
from ..test.FriendsMixIn import *
from ..test.LoginMixIn import *


class FriendAcceptedTest(TestCase, FriendsMixIn, LoginMixIn):

    def setUp(self):
        self.create_users()
        self.make_friends()
        self.create_invitations()
        self.login_user(username="TestUser8")

    def test_after_accepting_friend_inv_view_is_returned(self):
        form = self.valid_form()

        response = self.client.post(reverse('ask:friends.accept'), data=form)

        self.assertEqual(response.status_code, 200)

    def test_accepting_friend_changes_FriendModel(self):
        form = self.valid_form()

        response = self.client.post(reverse('ask:friends.accept'), data=form)

        friends = FriendsModel.objects.get(
            first=self.user8, second=self.user2)
        self.assertTrue(friends.accepted)

    def test_accepting_friend_changes_FriendModel_symmetrical(self):
        form = self.valid_form(username="TestUser3")

        response = self.client.post(reverse('ask:friends.accept'), data=form)

        friends = FriendsModel.objects.get(
            first=self.user3, second=self.user8)
        self.assertTrue(friends.accepted)

    def valid_form(self, username="TestUser2"):
        user = UserModel.objects.get(username=username)
        return {"user_id": user.id}
