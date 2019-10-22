from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic.edit import FormView, FormMixin
from django.shortcuts import reverse

from .forms import AnswerForm, QuestionForm, SignUpForm, FriendAcceptedForm, FriendSearchForm
from .models import UserModel, AnswerModel, QuestionModel, FriendsModel


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
        if type(user_id) == int:
            user = UserModel.objects.get(pk=user_id)
        elif type(user_id) == str:
            user = UserModel.objects.get(pk=user_id)
        else:
            user = user_id
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
        if type(user_id) == int:
            user = UserModel.objects.get(pk=user_id)
        elif type(user_id) == str:
            user = UserModel.objects.get(pk=user_id)
        else:
            user = user_id
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


def index(request):
    return render(request, "ask/index.html")


class CustomLoginView(LoginView):

    def form_valid(self, form):
        self.request.session['logged_in'] = True
        self.request.session['username'] = form.cleaned_data['username']
        return super().form_valid(form)


class CustomLogoutView(LogoutView):

    def post(self, request, *args, **kwargs):
        del request['logged_in']
        del request['username']
        super().post(request, *args, **kwargs)


class SignUpView(FormView):
    template_name = 'ask/signup.html'
    form_class = SignUpForm
    success_url = 'profile'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = self.form_to_model(form)
            user.set_password(form.cleaned_data['password'])
            user.save()
            self.log_in(user.username, form.cleaned_data['password'], request)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_to_model(self, form):
        clean_data = form.cleaned_data
        userdata = {
            'first_name': clean_data['first_name'],
            'last_name': clean_data['last_name'],
            'username': clean_data['username'],
            'email': clean_data['email'],
        }
        return UserModel(**userdata)

    def log_in(self, username, password, request):
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

        request.session['logged_in'] = True
        request.session['username'] = username


class ProfileView(View, QuestionsMixIn, FriendsMixIn):

    def get(self, request):
        if not self.is_user_logged_in(request.session):
            return HttpResponseRedirect(reverse("ask:login"))

        user_id = request.session['_auth_user_id']
        context = self.get_context(user_id)
        return render(request, "ask/profile.html", context=context)

    def is_user_logged_in(self, session):
        try:
            if session['logged_in']:
                return True
        except KeyError:
            return False
        else:
            return False

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    def get_context(self, user_id):
        user = UserModel.objects.get(pk=user_id)
        questions_with_answers = self.questions_with_answers(
            user)
        context = {"questions_with_answers": questions_with_answers}
        return context


class UserView(View, FormMixin, QuestionsMixIn, FriendsMixIn):
    form_class = QuestionForm

    def get(self, request, username):
        context = self.get_context(
            request.session['_auth_user_id'], username)
        return render(request, "ask/user.html", context=context)

    def post(self, request, username):
        form = self.get_form()
        context = self.get_context(
            request.session['_auth_user_id'], username)
        if form.is_valid():
            if form.cleaned_data['action'] == 'ask_question':
                self.create_question(
                    username,
                    request.session['_auth_user_id'],
                    form.cleaned_data['question_content'])
                context['question_submitted'] = "Your question was submitted"
            elif form.cleaned_data['action'] == 'add_friend':
                context['is_friend'] = True
                self.add_friend(request.session['_auth_user_id'], username)
            elif form.cleaned_data['action'] == 'remove_friend':
                context['is_friend'] = False
                self.remove_friend(request.session['_auth_user_id'], username)
        return render(request, "ask/user.html", context=context)

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    def get_context(self, logedin_user_id, username):
        viewed_user = UserModel.objects.get(username=username)
        questions_with_answers = self.questions_with_answers(viewed_user)
        is_friend_is_accepted = self.is_friend_is_accepted(
            logedin_user_id, viewed_user)
        context = {
            'username': username,
            'questions_with_answers': questions_with_answers,
            'is_friend': is_friend_is_accepted[0],
            'accepted': is_friend_is_accepted[1],
        }
        return context

    def is_friend_is_accepted(self, logedin_user_id, viewed_user):
        logedin_user = UserModel.objects.get(pk=logedin_user_id)

        try:
            friends = FriendsModel.objects.get(
                first=logedin_user, second=viewed_user)
        except FriendsModel.DoesNotExist:
            try:
                friends = FriendsModel.objects.get(
                    first=viewed_user, second=logedin_user)
            except FriendsModel.DoesNotExist:
                return False, False
            else:
                return True, friends.accepted
        else:
            return True, friends.accepted

    def create_question(self, owner_username, logedin_user_id, content):
        asked_by = UserModel.objects.filter(pk=logedin_user_id)[0]
        owner = UserModel.objects.filter(username=owner_username)[0]
        question = QuestionModel(owner=owner,
                                 asked_by=asked_by,
                                 content=content)
        question.save()

    def add_friend(self, logedin_user_id, username):
        logged_in_user = UserModel.objects.get(pk=logedin_user_id)
        viewed_user = UserModel.objects.get(username=username)
        friend = FriendsModel(first=logged_in_user, second=viewed_user)
        friend.save()

    def remove_friend(self, logedin_user_id, username):
        logged_in_user = UserModel.objects.get(pk=logedin_user_id)
        viewed_user = UserModel.objects.get(username=username)
        FriendsModel.objects.filter(
            first=logged_in_user, second=viewed_user).delete()
        FriendsModel.objects.filter(
            first=viewed_user, second=logged_in_user).delete()


class UnansweredView(View, FormMixin, QuestionsMixIn, FriendsMixIn):
    form_class = AnswerForm

    def get(self, request):
        try:
            user = UserModel.objects.filter(
                pk=request.session['_auth_user_id'])[0]
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        context = self.get_context(user)
        return render(request, 'ask/unanswered.html', context=context)

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    def get_context(self, user):
        unanswered_questions = self.unanswered_questions(user)
        unanswered_questions = unanswered_questions.order_by('date')[::-1]
        context = {'unanswered_questions': unanswered_questions}
        return context

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            answer = self.create_answer(form.cleaned_data['answer_content'])
            self.attach_answer_to_question(
                answer, form.cleaned_data['question_id'])

        return self.get(request)

    def create_answer(self, content):
        answer = AnswerModel(content=content)
        answer.save()
        return answer

    def attach_answer_to_question(self, answer, user_id):
        question = QuestionModel.objects.get(id=user_id)
        question.answer = answer
        question.save()


class FriendsView(View, QuestionsMixIn, FriendsMixIn):

    def get(self, request):
        try:
            user = UserModel.objects.get(
                pk=request.session['_auth_user_id'])
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        context = self.get_context(user, request)
        return render(request, "ask/friends.html", context=context)

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    def get_context(self, user, request):
        last_token = request.path.split('/')[-1]

        if last_token == 'inv' or last_token == 'accept':
            context = {
                'show_invites': True,
                'invitations': self.user_friends(user, accepted=False),
            }
        else:
            friends = self.friends_ordered(user, last_token)
            context = {"friends": friends}
        return context

    def friends_ordered(self, user, request_type):
        if request_type == 'recent':
            return self.order_by_date(user)[::-1]
        elif request_type == 'alph':
            return self.order_by_alphabet(user)
        else:
            return self.user_friends(user)

    def order_by_date(self, user):
        date = [f.date for f in user.friendsmodel_set.all()]
        second_date = [f.date for f in user.friends_second.all()]
        friends_with_date = list(
            zip(self.user_friends(user), date + second_date))
        friends_with_date.sort(key=lambda t: t[1].time())
        friends = [t[0] for t in friends_with_date]
        return friends

    def order_by_alphabet(self, user):
        friends = self.user_friends(user)
        friends.sort(key=lambda f: f.username)
        return friends


class FriendAcceptedView(View, FormMixin):
    form_class = FriendAcceptedForm

    def post(self, request):
        form = self.get_form()

        if form.is_valid():
            self.find_users_and_accept(request.session['_auth_user_id'],
                                       form.cleaned_data['user_id'])

        return FriendsView().get(request)

    def find_users_and_accept(self, user1_id, user2_id):
        user_first = UserModel.objects.get(pk=user1_id)
        user_second = UserModel.objects.get(pk=user2_id)

        try:
            self.accept_invitation(user_second, user_first)
        except FriendsModel.DoesNotExist:
            self.accept_invitation(user_first, user_second)

    def accept_invitation(self, user1, user2):
        friends = FriendsModel.objects.get(first=user1, second=user2)
        friends.accepted = True
        friends.save()


class FriendSearchView(View, QuestionsMixIn, FriendsMixIn, FormMixin):
    form_class = FriendSearchForm

    def post(self, request):
        try:
            user = UserModel.objects.get(
                pk=request.session['_auth_user_id'])
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        context = self.get_context(user, request)
        return render(request, "ask/friends.html", context=context)

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    def get_context(self, user, request):
        form = self.get_form()
        context = {}
        if form.is_valid():
            searched_user = form.cleaned_data['search_text']
            context = {'friends': self.get_matching_friends(
                user, searched_user)}
        return context

    def get_matching_friends(self, user, searched_user):
        friends = self.user_friends(user)
        return [f for f in friends if searched_user in f.username]
