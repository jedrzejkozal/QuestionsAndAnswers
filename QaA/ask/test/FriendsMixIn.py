from ..models import UserModel, FriendsModel


class FriendsMixIn:

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
