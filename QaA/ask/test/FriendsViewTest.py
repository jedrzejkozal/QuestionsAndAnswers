from django.shortcuts import reverse
from django.test import TestCase

from ..test.FriendsMixIn import *


class FriendsViewTest(TestCase, FriendsMixIn):

    def setUp(self):
        self.create_users()
        self.make_friends()
        self.create_invitations()

    def test_friends_relation_is_mutual(self):
        self.assertEqual(
            self.user1, self.user2.friends_second.all()[0].first)
        self.assertEqual(self.user2, self.user1.friends.all()[0])

    def test_GET_all_friends_are_returned(self):
        self.log_in(user_id=1)

        response = self.client.get(reverse('ask:friends'))

        self.assertEqual(list(response.context['friends']),
                         [self.user2, self.user3, self.user5])

    def test_GET_all_friends_of_user2_are_returned(self):
        self.log_in(user_id=2)

        response = self.client.get(reverse('ask:friends'))

        self.assertEqual(list(response.context['friends']),
                         [self.user4, self.user1, self.user5])

    def test_GET_recently_added_returns_sorted_friends_user1(self):
        self.log_in(user_id=1)

        response = self.client.get(reverse('ask:friends.recent'))

        self.assertEqual(list(response.context['friends']),
                         [self.user5, self.user3, self.user2])

    def test_GET_recently_added_returns_sorted_friends_user2(self):
        self.log_in(user_id=2)

        response = self.client.get(reverse('ask:friends.recent'))

        self.assertEqual(list(response.context['friends']),
                         [self.user5, self.user4, self.user1])

    def test_GET_recently_added_returns_sorted_friends_user5(self):
        self.log_in(user_id=5)

        response = self.client.get(reverse('ask:friends.recent'))

        self.assertEqual(list(response.context['friends']),
                         [self.user6, self.user4, self.user3, self.user2, self.user1])

    def test_GET_in_alphabetical_order_user1(self):
        self.log_in(user_id=1)

        response = self.client.get(reverse('ask:friends.alph'))

        self.assertEqual(list(response.context['friends']),
                         [self.user2, self.user3, self.user5])

    def test_GET_in_alphabetical_order_user2(self):
        self.log_in(user_id=2)

        response = self.client.get(reverse('ask:friends.alph'))

        self.assertEqual(list(response.context['friends']),
                         [self.user1, self.user4, self.user5])

    def test_GET_in_alphabetical_order_user5(self):
        self.log_in(user_id=5)

        response = self.client.get(reverse('ask:friends.alph'))

        self.assertEqual(list(response.context['friends']),
                         [self.user1, self.user2, self.user3, self.user4, self.user6])

    def test_GET_inv_call_context_show_invites_eq_True(self):
        self.log_in(user_id=1)

        response = self.client.get(reverse('ask:friends.inv'))

        self.assertEqual(response.context['show_invites'], True)

    def test_GET_inv_no_invitations_empty_query(self):
        self.log_in(user_id=1)

        response = self.client.get(reverse('ask:friends.inv'))

        self.assertEqual(list(response.context['invitations']), [])

    def test_GET_inv_context_invitations_for_user2(self):
        self.log_in(user_id=2)

        response = self.client.get(reverse('ask:friends.inv'))

        self.assertEqual(list(response.context['invitations']), [self.user8])

    def test_GET_inv_context_invitations_for_user8(self):
        self.log_in(user_id=8)

        response = self.client.get(reverse('ask:friends.inv'))

        self.assertEqual(list(response.context['invitations']), [
                         self.user2, self.user5, self.user6, self.user3])

    def test_GET_inv_context_invitations_for_user6(self):
        self.log_in(user_id=6)

        response = self.client.get(reverse('ask:friends.inv'))

        self.assertEqual(list(response.context['invitations']), [
                         self.user8, self.user4])
