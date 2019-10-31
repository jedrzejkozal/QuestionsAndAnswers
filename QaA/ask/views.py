from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic.base import View
from django.views.generic.edit import FormMixin, FormView

from .forms import AnswerForm, QuestionForm, SignUpForm
from .models import AnswerModel, FriendsModel, UserModel
from .view.MixIns import *


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
            send_mail("Account created in Questions&Answers",
                      "Thank you for creating account",
                      "from@example.com",
                      [user.email],
                      fail_silently=False)
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
        try:
            user = UserModel.objects.get(
                pk=request.session['_auth_user_id'])
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        context = self.get_context(user)
        self.add_pagination(context, request)
        return render(request, "ask/profile.html", context=context)

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    def get_context(self, user):
        questions_with_answers = self.questions_with_answers(
            user)
        context = {"questions_with_answers": questions_with_answers}
        return context

    def add_pagination(self, context, request):
        paginator = Paginator(context["questions_with_answers"], 6)
        page = request.GET.get('page')
        context["questions_with_answers"] = paginator.get_page(page)


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
            self.dispatch_action(form.cleaned_data, context,
                                 username, request.session['_auth_user_id'])
        return render(request, "ask/user.html", context=context)

    def dispatch_action(self, cleaned_data, context, username, auth_user_id):
        if cleaned_data['action'] == 'ask_question':
            context['question_submitted'] = "Your question was submitted"
            self.create_question(username, auth_user_id,
                                 cleaned_data['question_content'])
        elif cleaned_data['action'] == 'add_friend':
            context['is_friend'] = True
            self.add_friend(auth_user_id, username)
        elif cleaned_data['action'] == 'remove_friend':
            context['is_friend'] = False
            self.remove_friend(auth_user_id, username)

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
            user = UserModel.objects.get(
                pk=request.session['_auth_user_id'])
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
