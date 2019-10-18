
from django.shortcuts import reverse
from django.test.testcases import TestCase

from ..test.QuestionsMixIn import *


class UserViewTest(TestCase, QuestionsMixIn):
    url = reverse('ask:user', args=('TestUser2',))

    def test_context_contains_viewed_user_username(self):
        self.create_users()
        response = self.client.get(self.url)

        self.assertEqual(response.context['username'], 'TestUser2')

    def test_username_is_redered_in_template(self):
        self.create_users()
        response = self.client.get(self.url)

        self.assertContains(response, 'TestUser2')

    def test_context_contains_user_questions(self):
        self.create_users()
        self.create_question1(with_answer=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question1, self.answer1)])

    def test_context_multiple_questions_are_ordered_by_newest(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2(with_answer=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question2, self.answer2), (self.question1, self.answer1)])

    def test_questions_of_other_users_are_not_in_query(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question3(with_answer=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question1, self.answer1)])

    def test_only_answered_questions_are_in_query(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2()

        response = self.client.get(self.url)

        self.assertEqual(response.context['questions_with_answers'],
                         [(self.question1, self.answer1)])

    def test_template_rendered_with_questions_contents(self):
        self.create_users()
        self.create_question1(with_answer=True)
        self.create_question2(with_answer=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What is the meaning of everything?")

    def test_template_rendered_with_answer_contents(self):
        self.create_users()
        self.create_question1(with_answer=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "42")

    def test_POST_new_question_is_created_in_database(self):
        self.create_users()
        self.login_user(user_id=1)
        form = self.get_valid_form()
        response = self.client.post(self.url, data=form)

        self.assertEqual(len(QuestionModel.objects.all()), 1)

    def test_POST_new_question_is_created_with_valid_content(self):
        self.create_users()
        self.login_user(user_id=1)
        form = self.get_valid_form()

        response = self.client.post(self.url, data=form)

        last_question = QuestionModel.objects.all()[0]
        self.assertEqual(last_question.content, 'question test content')

    def test_POST_posted_question_have_answer(self):
        self.create_users()
        self.login_user(user_id=1)
        form = self.get_valid_form()

        response = self.client.post(self.url, data=form)

        last_question = QuestionModel.objects.all()[0]
        self.assertEqual(last_question.answer, None)

    def test_POST_question_asked_by_logged_in_user(self):
        self.create_users()
        self.login_user(user_id=1)
        form = self.get_valid_form()

        response = self.client.post(self.url, data=form)

        last_question = QuestionModel.objects.all().order_by('date')[0]
        self.assertEqual(last_question.asked_by, self.test_user1)

    def test_POST_question_owner_is_valid(self):
        self.create_users()
        self.login_user(user_id=1)
        form = self.get_valid_form()

        response = self.client.post(self.url, data=form)

        last_question = QuestionModel.objects.all()[0]
        self.assertEqual(last_question.owner, self.test_user2)

    def test_POST_after_submiting_valid_form_message_is_in_context(self):
        self.create_users()
        self.login_user(user_id=1)
        form = self.get_valid_form()

        response = self.client.post(self.url, data=form)

        self.assertEqual(
            response.context['question_submitted'], "Your question was submitted")

    def test_POST_form_is_invalid_question_not_created(self):
        self.create_users()
        self.login_user(user_id=1)
        form = self.get_valid_form()
        form['question_content'] = ''

        response = self.client.post(self.url, data=form)

        questions = QuestionModel.objects.all()
        self.assertEqual(len(questions), 0)

    def get_valid_form(self):
        form = {'question_content': 'question test content'}
        return form
