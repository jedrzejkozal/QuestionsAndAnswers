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

    def test_username_already_taken(self):
        User.objects.create_user("jj")
        form_input = self.valid_form()
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(response, "form", "username",
                             "Username already taken")

    def test_email_already_taken(self):
        User.objects.create_user("otherUser", email="some1@email.com")
        form_input = self.valid_form()
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(response, "form", "email",
                             "Email address already taken")

    def test_to_short_password_form_is_invalid(self):
        request = self.factory.post('ask/signup', data={'password': 'qwe1#'})

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        response.context = response.context_data
        self.assertFormError(response, "form", "password",
                             "Password to short. Must be at least 6 characters long")

    def test_password_and_password_repeat_does_not_match(self):
        form_input = self.valid_form()
        form_input['password_repeat'] = 'aaa@41'
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(
            response, "form", "password_repeat", "Password does not match")

    def test_password_does_not_contain_special_characters_form_is_invalid(self):
        form_input = self.valid_form()
        form_input['password'] = "aaaa41"
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(
            response, "form", "password",
            ["['Password must contain at least one special character']"])

    def test_password_does_not_contain_numbers_form_is_invalid(self):
        form_input = self.valid_form()
        form_input['password'] = "aaaa#@"
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(
            response, "form", "password",
            ["['Password must contain at least one number']"])

    def test_password_to_similar_to_username_form_is_invalid(self):
        form_input = self.valid_form()
        form_input['password'] = "jjjj@1"
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(
            response, "form", "password",
            ["The password is too similar to the username"])

    def test_password_to_common_form_is_invalid(self):
        form_input = self.valid_form()
        form_input['password'] = "qwerty"
        request = self.factory.post('ask/signup', data=form_input)

        response = SignUpView.as_view()(request)

        response.context = response.context_data
        self.assertFormError(
            response, "form", "password",
            ["['Password must contain at least one special character', 'Password must contain at least one number', 'This password is too common.']"])

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

        queryset = User.objects.filter(username='jj')
        self.assertEqual(queryset[0].first_name, 'JJ')

    def valid_form(self):
        return {'first_name': 'JJ',
                'last_name': 'Goatl',
                'username': 'jj',
                'password': 'svm@43',
                'password_repeat': 'svm@43',
                'email': 'some1@email.com'}
