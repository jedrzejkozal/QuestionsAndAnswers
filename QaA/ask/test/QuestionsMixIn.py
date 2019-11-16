from ..models import UserModel, AnswerModel, QuestionModel


class QuestionsMixIn:

    def create_users(self):
        self.test_user1 = UserModel(username="TestUser1")
        self.test_user1.save()
        self.test_user2 = UserModel(username="TestUser2")
        self.test_user2.save()
        self.test_user3 = UserModel(username="TestUser3")
        self.test_user3.save()

    def create_question1(self, with_answer=False):
        if with_answer:
            self.create_answer1()
            answer = self.answer1
        else:
            answer = None
        self.question1 = QuestionModel(
            asked_by=self.test_user1, owner=self.test_user2, content="Test Question 1", answer=answer)
        self.question1.save()

    def create_question2(self, with_answer=False):
        if with_answer:
            self.create_answer2()
            answer = self.answer2
        else:
            answer = None
        self.question2 = QuestionModel(
            asked_by=self.test_user3, owner=self.test_user2, content="Test Question 2", answer=answer)
        self.question2.save()

    def create_question3(self, with_answer=False):
        if with_answer:
            self.create_answer3()
            answer = self.answer3
        else:
            answer = None
        self.question3 = QuestionModel(
            asked_by=self.test_user1, owner=self.test_user3, content="Test Question 3", answer=answer)

    def create_answer1(self):
        self.answer1 = AnswerModel(content="Test Answer 1")
        self.answer1.save()

    def create_answer2(self):
        self.answer2 = AnswerModel(content="Test Answer 2")
        self.answer2.save()

    def create_answer3(self):
        self.answer3 = AnswerModel(content="Test Answer 3")
        self.answer3.save()
