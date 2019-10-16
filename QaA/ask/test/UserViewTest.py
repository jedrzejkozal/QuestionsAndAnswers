from django.test import TestCase, RequestFactory
from django.http.response import HttpResponse
from ..views import UserView
from ..models import QuestionModel, AnswerModel
from django.contrib.auth.models import User
from django.urls import reverse


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

    def test_context_contains_user_questions(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.login_user(user_id=2)

        response = self.client.get(reverse('ask:user'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question1, self.answer1)])

    def test_context_multiple_questions_are_ordered_by_newest(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2(with_answer=True)
        self.login_user(user_id=2)

        response = self.client.get(reverse('ask:user'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question2, self.answer2), (self.question1, self.answer1)])

    def test_questions_of_other_users_are_not_in_query(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question3(with_answer=True)
        self.login_user(user_id=2)

        response = self.client.get(reverse('ask:user'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question1, self.answer1)])

    def test_only_answered_questions_are_in_query(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2()
        self.login_user(user_id=2)

        response = self.client.get(reverse('ask:user'))

        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question1, self.answer1)])

    def test_template_rendered_with_questions_contents(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2(with_answer=True)
        self.login_user(user_id=2)

        response = self.client.get(reverse('ask:user'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What is the meaning of everything?")

    def test_template_rendered_with_answer_contents(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.login_user(user_id=2)

        response = self.client.get(reverse('ask:user'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "42")

    def test_num_of_unanswered_is_passed_in_context(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2()
        self.login_user(user_id=2)

        response = self.client.get(reverse('ask:user'))

        self.assertEqual(response.context['num_unanswered'], 1)

    def create_users(self):
        self.test_user1 = User(username="TestUser1")
        self.test_user1.save()
        self.test_user2 = User(username="TestUser2")
        self.test_user2.save()
        self.test_user3 = User(username="TestUser3")
        self.test_user3.save()

    def create_question1(self, with_answer=False):
        if with_answer:
            self.create_answer1()
            answer = self.answer1
        else:
            answer = None
        self.question1 = QuestionModel(
            asked_by=self.test_user1, owner=self.test_user2, content="What is the meaning of everything?", answer=answer)
        self.question1.save()

    def create_question2(self, with_answer=False):
        if with_answer:
            self.create_answer2()
            answer = self.answer2
        else:
            answer = None
        self.question2 = QuestionModel(
            asked_by=self.test_user3, owner=self.test_user2, content="What's up?", answer=answer)
        self.question2.save()

    def create_question3(self, with_answer=False):
        if with_answer:
            self.create_answer3()
            answer = self.answer3
        else:
            answer = None
        self.question3 = QuestionModel(
            asked_by=self.test_user1, owner=self.test_user3, content="Does Marcellus look like a b?", answer=answer)

    def create_answer1(self):
        self.answer1 = AnswerModel(content="42")
        self.answer1.save()

    def create_answer2(self):
        self.answer2 = AnswerModel(content="Not much")
        self.answer2.save()

    def create_answer3(self):
        self.answer3 = AnswerModel(content="Not much")
        self.answer3.save()

    def login_user(self, user_id=2):
        session = self.client.session
        session['logged_in'] = True
        session['_auth_user_id'] = user_id
        session.save()
