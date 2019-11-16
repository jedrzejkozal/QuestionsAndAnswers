from django.http.response import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..test.QuestionsMixIn import *
from ..test.LoginMixIn import *
from ..views import ProfileView


class ProfileViewTest(TestCase, QuestionsMixIn, LoginMixIn):

    def setUp(self):
        self.factory = RequestFactory()

    def test_user_not_logged_in_redirect_to_loggin_page(self):
        request = self.factory.get('ask/user')
        request.session = {}

        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponse)

    def test_user_not_logged_out_redirect_to_loggin_page(self):
        request = self.factory.get('ask/user')
        request.session = {'logged_in': False}

        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponse)

    def test_context_contains_user_questions(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.login_user(username="TestUser2")

        response = self.client.get(reverse('ask:profile'))
        questions_with_answers = response.context['questions_with_answers']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(questions_with_answers[0][0], self.question1)
        self.assertEqual(questions_with_answers[0][1], self.answer1)

    def test_context_multiple_questions_are_ordered_by_newest(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2(with_answer=True)
        self.login_user(username="TestUser2")

        response = self.client.get(reverse('ask:profile'))
        questions_with_answers = response.context['questions_with_answers']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(questions_with_answers[0][0], self.question2)
        self.assertEqual(questions_with_answers[0][1], self.answer2)
        self.assertEqual(questions_with_answers[1][0], self.question1)
        self.assertEqual(questions_with_answers[1][1], self.answer1)

    def test_questions_of_other_users_are_not_in_query(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question3(with_answer=True)
        self.login_user(username="TestUser2")

        response = self.client.get(reverse('ask:profile'))
        questions_with_answers = response.context['questions_with_answers']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(questions_with_answers[0][0], self.question1)
        self.assertEqual(questions_with_answers[0][1], self.answer1)

    def test_only_answered_questions_are_in_query(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2()
        self.login_user(username="TestUser2")

        response = self.client.get(reverse('ask:profile'))
        questions_with_answers = response.context['questions_with_answers']

        self.assertEqual(questions_with_answers[0][0], self.question1)
        self.assertEqual(questions_with_answers[0][1], self.answer1)

    def test_template_rendered_with_questions_contents(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2(with_answer=True)
        self.login_user(username="TestUser2")

        response = self.client.get(reverse('ask:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Question 1")

    def test_template_rendered_with_answer_contents(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.login_user(username="TestUser2")

        response = self.client.get(reverse('ask:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Answer 1")

    def test_num_of_unanswered_is_passed_in_context(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2()
        self.login_user(username="TestUser2")

        response = self.client.get(reverse('ask:profile'))

        self.assertEqual(response.context['num_unanswered'], 1)
