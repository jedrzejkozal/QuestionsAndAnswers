from django.shortcuts import reverse
from django.test import TestCase

from ..test.FriendsMixIn import *
from ..test.LoginMixIn import *


class FriendSearchViewTest(TestCase, FriendsMixIn, LoginMixIn):

    def setUp(self):
        self.create_users()
        self.make_friends()
        self.create_invitations()

    def test_search_for_user_with_no_friends_returns_empty_list(self):
        self.login_user(username="IhaveNoFriends")
        form = {'search_text': 'TestUser'}

        response = self.client.post(reverse('ask:friends.search'), data=form)

        self.assertEqual(list(response.context['friends']), [])

    def test_search_for_user2_returns_matching_users(self):
        self.login_user(username="TestUser2")
        form = {'search_text': 'TestUser'}

        response = self.client.post(reverse('ask:friends.search'), data=form)

        self.assertEqual(list(response.context['friends']), [
                         self.user4, self.user1, self.user5])

    def test_search_for_user2_with_one_matching_user_returns_one_user(self):
        self.login_user(username="TestUser2")
        form = {'search_text': 'TestUser4'}

        response = self.client.post(reverse('ask:friends.search'), data=form)

        self.assertEqual(list(response.context['friends']), [self.user4])

    def test_search_for_user2_invalid_searchtext_returns_empty_list(self):
        self.login_user(username="TestUser2")
        form = {'search_text': 'TestUser3'}

        response = self.client.post(reverse('ask:friends.search'), data=form)

        self.assertEqual(list(response.context['friends']), [])
