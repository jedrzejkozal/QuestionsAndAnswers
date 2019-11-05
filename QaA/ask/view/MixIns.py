from ..models import QuestionModel, UserModel


def get_user(user_id):
    if type(user_id) == int:
        user = UserModel.objects.get(pk=user_id)
    elif type(user_id) == str:
        user = UserModel.objects.get(pk=user_id)
    else:
        user = user_id
    return user


class QuestionsMixIn:

    def questions_with_answers(self, user):
        answered_questions = QuestionModel.objects.filter(
            owner=user).exclude(answer=None).order_by('date')[::-1]
        answers = [question.answer for question in answered_questions]
        return list(zip(answered_questions, answers))

    @staticmethod
    def add_num_unanswered_to_context(func, *args, **kwargs):
        def context_with_unanswered(self, *args, **kwargs):
            context = func(self, *args, **kwargs)
            user_id = args[0]
            context["num_unanswered"] = self.get_num_unanswered(user_id)
            return context
        return context_with_unanswered

    def get_num_unanswered(self, user_id):
        user = get_user(user_id)
        unanswered_questions = self.unanswered_questions(user)
        return len(unanswered_questions)

    def unanswered_questions(self, user):
        unanswered_questions = QuestionModel.objects.filter(
            owner=user).filter(answer=None)
        return unanswered_questions


class FriendsMixIn:

    @staticmethod
    def add_num_invites_to_context(func, *args, **kwargs):
        def context_with_invites(self, *args, **kwargs):
            context = func(self, *args, **kwargs)
            user_id = args[0]
            context["num_invites"] = self.get_num_invites(user_id)
            return context
        return context_with_invites

    def get_num_invites(self, user_id):
        user = get_user(user_id)
        user_invites = self.user_friends(user, accepted=False)
        return len(user_invites)

    def user_friends(self, user, accepted=True):
        friends = list(user.friends.all())
        second_friends = [f.first for f in user.friends_second.all()]
        friends_accepted = [f.accepted for f in user.friendsmodel_set.all()]
        second_accepted = [f.accepted for f in user.friends_second.all()]
        friends_with_accepted = list(
            zip(friends + second_friends, friends_accepted + second_accepted))
        filtered = filter(lambda t: t[1] == accepted, friends_with_accepted)

        return [f[0] for f in filtered]


class AvatarMinIn:

    @staticmethod
    def add_avatar_to_context(func, *args, **kwargs):
        def context_with_avatar(self, *args, **kwargs):
            context = func(self, *args, **kwargs)
            user = get_user(args[0])
            context['user_avatar'] = user.avatar
            return context
        return context_with_avatar
