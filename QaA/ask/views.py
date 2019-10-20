from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.shortcuts import reverse

from .forms import AnswerForm, QuestionForm, SignUpForm
from .models import UserModel, AnswerModel, QuestionModel


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


class QuestionsMixIn:

    def questions_with_answers(self, user):
        answered_questions = QuestionModel.objects.filter(
            owner=user).exclude(answer=None).order_by('date')[::-1]
        answers = [question.answer for question in answered_questions]
        return list(zip(answered_questions, answers))

    def unanswered_questions(self, user):
        unanswered_questions = QuestionModel.objects.filter(
            owner=user).filter(answer=None)
        return unanswered_questions


class ProfileView(View, QuestionsMixIn):

    def get(self, request):
        if not self.is_user_logged_in(request.session):
            return HttpResponseRedirect(reverse("ask:login"))
        context = self.get_context(request)
        return render(request, "ask/profile.html", context=context)

    def is_user_logged_in(self, session):
        try:
            if session['logged_in'] == False:
                return False
        except KeyError:
            return False
        else:
            return True

    def get_context(self, request):
        user_id = request.session['_auth_user_id']
        user = UserModel.objects.get(pk=user_id)
        questions_with_answers = self.questions_with_answers(
            user)
        num_unanswered = self.get_num_unanswered(user_id)
        context = {"questions_with_answers": questions_with_answers,
                   "num_unanswered": num_unanswered}
        return context

    def get_num_unanswered(self, user_id):
        user = UserModel.objects.get(pk=user_id)
        unanswered_questions = self.unanswered_questions(user)
        return len(unanswered_questions)


class UserView(FormView, QuestionsMixIn):
    form_class = QuestionForm

    def get(self, request, username):
        context = self.get_user_questions(username)
        return render(request, "ask/user.html", context=context)

    def post(self, request, username):
        form = self.get_form()
        context = self.get_user_questions(username)
        if form.is_valid():
            self.create_question(
                username, request.session['_auth_user_id'], form.cleaned_data['question_content'])
            context['question_submitted'] = "Your question was submitted"
        return render(request, "ask/user.html", context=context)

    def get_user_questions(self, username):
        user = UserModel.objects.get(username=username)
        questions_with_answers = self.questions_with_answers(user)
        context = {'username': username,
                   "questions_with_answers": questions_with_answers}
        return context

    def create_question(self, owner_username, logedin_user_id, content):
        asked_by = UserModel.objects.filter(pk=logedin_user_id)[0]
        owner = UserModel.objects.filter(username=owner_username)[0]
        question = QuestionModel(owner=owner,
                                 asked_by=asked_by,
                                 content=content)
        question.save()


class UnansweredView(FormView, QuestionsMixIn):
    form_class = AnswerForm

    def get(self, request):
        try:
            user = UserModel.objects.filter(
                pk=request.session['_auth_user_id'])[0]
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        unanswered_questions = self.unanswered_questions(user)
        unanswered_questions = unanswered_questions.order_by('date')[::-1]
        context = {'unanswered_questions': unanswered_questions}
        return render(request, 'ask/unanswered.html', context=context)

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


class FriendsView(View):

    def get(self, request):
        try:
            user = UserModel.objects.filter(
                pk=request.session['_auth_user_id'])[0]
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        friends = self.order_based_on_request(request, user)
        context = {"friends": friends}

        return render(request, "ask/friends.html", context=context)

    def order_based_on_request(self, request, user):
        last_token = request.path.split('/')[-1]

        if last_token == 'recent':
            return self.order_by_date(user)[::-1]
        elif last_token == 'alph':
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

    def user_friends(self, user):
        friends = user.friends.all()
        second_friends = [f.first for f in user.friends_second.all()]
        return list(friends) + second_friends
