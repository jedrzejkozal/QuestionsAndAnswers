from django.test import TestCase

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from .views import signup


class SignUpTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_no_username_request_rejected(self):
        request = self.factory.post('ask/signup')
        self.assertTrue(request.method == 'POST')
        response = signup(request)

        self.assertEqual(response.status_code, 400)
        # self.assertContains(response, "Username must be specified")


"""
Test cases to implement:
Passwords are not stored in plain text
Email is required
Username is taken
Email is taken
"""
