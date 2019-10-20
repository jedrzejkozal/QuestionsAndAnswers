
from django.shortcuts import reverse
from django.test import TestCase

from ..test.QuestionsMixIn import *
from ..models import FriendsModel


class FriendAcceptedTest(TestCase, QuestionsMixIn):

    def setUp(self):
        self.create_users()
        self.test_user1.friends.add(self.test_user2)
        self.test_user2.friends.add(self.test_user3)
        self.login_user(user_id=2)

    def test_after_accepting_friend_inv_view_is_returned(self):
        form = self.valid_form()

        response = self.client.post(reverse('ask:friends.accept'), data=form)

        self.assertEqual(response.status_code, 200)

    def test_accepting_friend_changes_FriendModel(self):
        form = self.valid_form()

        response = self.client.post(reverse('ask:friends.accept'), data=form)

        friends = FriendsModel.objects.get(
            first=self.test_user1, second=self.test_user2)
        self.assertTrue(friends.accepted)

    def test_accepting_friend_changes_FriendModel_symmetrical(self):
        form = self.valid_form(user_id=3)

        response = self.client.post(reverse('ask:friends.accept'), data=form)

        friends = FriendsModel.objects.get(
            first=self.test_user2, second=self.test_user3)
        self.assertTrue(friends.accepted)

    def valid_form(self, user_id=1):
        return {"user_id": user_id}
