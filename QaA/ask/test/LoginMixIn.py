from ..models import UserModel


class LoginMixIn:

    def login_user(self, username="TestUser2"):
        user = UserModel.objects.get(username=username)
        self.client.force_login(user)

        session = self.client.session
        session['logged_in'] = True
        session['_auth_user_id'] = user.id
        session.save()
