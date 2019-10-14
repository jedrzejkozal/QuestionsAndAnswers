from django.test import TestCase

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect

from .views import SignUpView


class SignUpTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_no_first_name_form_is_invalid(self):
        request = self.factory.post('ask/signup')

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        response.context = response.context_data
        self.assertFormError(response, "form", "first_name",
                             "This field is required.")

    def test_no_last_name_form_is_invalid(self):
        request = self.factory.post('ask/signup')

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        response.context = response.context_data
        self.assertFormError(response, "form", "last_name",
                             "This field is required.")

    def test_no_username_form_is_invalid(self):
        request = self.factory.post('ask/signup')

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        response.context = response.context_data
        self.assertFormError(response, "form", "username",
                             "This field is required.")

    def test_no_password_form_is_invalid(self):
        request = self.factory.post('ask/signup')

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        response.context = response.context_data
        self.assertFormError(response, "form", "password",
                             "This field is required.")

    def test_no_email_form_is_invalid(self):
        request = self.factory.post('ask/signup')

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        response.context = response.context_data
        self.assertFormError(response, "form", "email",
                             "This field is required.")

    def test_to_short_password_form_is_invalid(self):
        request = self.factory.post('ask/signup', data={'password': 'qwert'})

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        response.context = response.context_data
        self.assertFormError(response, "form", "password",
                             "Password to short. Must be at least 6 characters long")

    def test_username_already_taken(self):
        User.objects.create_user("jj")
        form_input = self.valid_form()
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(response, "form", "username",
                             "Username already taken")

    def valid_form(self):
        return {'first_name': 'JJ',
                'last_name': 'Goatl',
                'username': 'jj',
                'password': 'svm@43',
                'email': 'cool@email.com'}

    def test_form_correct_user_redirected(self):
        form_input = self.valid_form()
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_form_correct_user_is_created(self):
        form_input = self.valid_form()
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        o = User.objects.filter(username='jj')
        self.assertEqual(o[0].first_name, 'JJ')


"""
Test cases to implement:
Username is taken
Email is taken
"""
