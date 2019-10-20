from django.shortcuts import reverse
from django.test import TestCase

from ..test.QuestionsMixIn import *


class UnansweredViewTest(TestCase, QuestionsMixIn):
    url = reverse('ask:unanswered')

    def test_GET_questions_are_in_context(self):
        self.create_users()
        self.create_question1()
        self.login_user(user_id=2)

        response = self.client.get(self.url)

        self.assertEqual(list(response.context['unanswered_questions']),
                         [self.question1])

    def test_GET_only_unanswered_questions_are_in_context(self):
        self.create_users()
        self.create_question1()
        self.create_question2(with_answer=True)
        self.login_user(user_id=2)

        response = self.client.get(self.url)

        self.assertEqual(list(response.context['unanswered_questions']),
                         [self.question1])

    def test_GET_unanswered_questions_are_in_right_order(self):
        self.create_users()
        self.create_question1()
        self.create_question2()
        self.login_user(user_id=2)

        response = self.client.get(self.url)

        self.assertEqual(list(response.context['unanswered_questions']),
                         [self.question2, self.question1])

    def test_GET_no_unanswered_questions_context_variable_empty(self):
        self.create_users()
        self.login_user(user_id=2)

        response = self.client.get(self.url)

        self.assertEqual(list(response.context['unanswered_questions']), [])

    def test_POST_form_valid_answer_for_selected_question_is_created(self):
        self.create_users()
        self.create_question1()
        self.login_user(user_id=2)
        form = self.valid_form()

        response = self.client.post(self.url, data=form)

        question = QuestionModel.objects.get(pk=1)
        answer = AnswerModel.objects.get(pk=1)
        self.assertEqual(question.answer, answer)

    def test_POST_form_invalid_answer_not_created(self):
        self.create_users()
        self.create_question1()
        self.login_user(user_id=2)
        form = self.valid_form()
        form['answer_content'] = ''

        response = self.client.post(self.url, data=form)

        question = QuestionModel.objects.get(pk=1)
        self.assertEqual(question.answer, None)

    def valid_form(self, question_id=1):
        return {
            'answer_content': 'Test answer',
            'question_id': question_id
        }
