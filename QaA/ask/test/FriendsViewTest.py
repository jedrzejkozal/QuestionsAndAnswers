from django.test import TestCase
from ..models import UserModel, FriendsModel

from django.shortcuts import reverse


class FriendsViewTest(TestCase):

    def setUp(self):
        self.create_users()
        self.make_friends()
        self.create_invitations()

    def create_users(self):
        self.user1 = self.create_user(
            username="TestUser1", email="test1@email.com", password="asda%4")
        self.user2 = self.create_user(
            username="TestUser2", email="test2@email.com", password="asda%4")
        self.user3 = self.create_user(
            username="TestUser3", email="test3@email.com", password="asda%4")
        self.user4 = self.create_user(
            username="TestUser4", email="test4@email.com", password="asda%4")
        self.user5 = self.create_user(
            username="TestUser5", email="test5@email.com", password="asda%4")
        self.user6 = self.create_user(
            username="TestUser6", email="test6@email.com", password="asda%4")
        self.user7 = self.create_user(
            username="IhaveNoFriends", email="iamso@lonley.com", password="asda%4")
        self.user8 = self.create_user(
            username="TestUser8", email="test8@email.com", password="asda%4")

    def create_user(self, username, email, password):
        user = UserModel(username=username,
                         email=email,
                         password=password)
        user.save()
        return user

    def make_friends(self):
        self.user1.friends.add(self.user2)
        self.user1.friends.add(self.user3)
        self.user2.friends.add(self.user4)

        self.user5.friends.add(self.user1)
        self.user5.friends.add(self.user2)
        self.user3.friends.add(self.user5)
        self.user5.friends.add(self.user4)
        self.user6.friends.add(self.user5)

        friends = FriendsModel.objects.all()
        for f in friends:
            f.accepted = True
            f.save()

    def create_invitations(self):
        self.user8.friends.add(self.user2)
        self.user3.friends.add(self.user8)
        self.user8.friends.add(self.user5)
        self.user8.friends.add(self.user6)

        self.user4.friends.add(self.user6)

    def log_in(self, user_id=1):
        session = self.client.session
        session['logged_in'] = True
        session['_auth_user_id'] = user_id
        session.save()

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
