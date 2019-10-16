from django.test import TestCase, RequestFactory
from django.http.response import HttpResponse
from ..views import UserView


class UserViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_user_not_logged_in_redirect_to_loggin_page(self):
        request = self.factory.get('ask/user')
        request.session = {}

        response = UserView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponse)

    def test_user_not_logged_out_redirect_to_loggin_page(self):
        request = self.factory.get('ask/user')
        request.session = {'logged_in': False}

        response = UserView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponse)
