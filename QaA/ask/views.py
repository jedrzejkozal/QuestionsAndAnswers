from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.contrib.auth import login, authenticate

from .models import QuestionModel, AnswerModel

from .forms import SignUpForm, QuestionForm


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
        return User(**userdata)

    def log_in(self, username, password, request):
        user = authenticate(request, username=username, password=password)
        print('\nauthenticate user ', user)
        if user:
            print('\nauthenticate call reutrned user')
            # request.user = user
            login(request, user)

        request.session['logged_in'] = True
        request.session['username'] = username


class ProfileView(View):

    def get(self, request):
        print('_auth_user_id', request.session['_auth_user_id'])
        if not self.is_user_logged_in(request.session):
            return HttpResponseRedirect("ask/login.html")
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
        user = User.objects.get(pk=user_id)
        questions_with_answers = self.get_answered_questions_with_answers(
            user)
        num_unanswered = self.get_num_unanswered(user_id)
        context = {"questions_with_answers": questions_with_answers,
                   "num_unanswered": num_unanswered}
        return context

    def get_answered_questions_with_answers(self, user):
        answered_questions = QuestionModel.objects.filter(
            owner=user).exclude(answer=None).order_by('date')[::-1]
        answers = [question.answer for question in answered_questions]
        return list(zip(answered_questions, answers))

    def get_num_unanswered(self, user_id):
        user = User.objects.get(pk=user_id)
        unanswered_questions = QuestionModel.objects.filter(
            owner=user).filter(answer=None)
        return len(unanswered_questions)


class UserView(FormView):
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
        user = User.objects.get(username=username)
        questions_with_answers = ProfileView().get_answered_questions_with_answers(user)
        context = {'username': username,
                   "questions_with_answers": questions_with_answers}
        return context

    def create_question(self, owner_username, logedin_user_id, content):
        asked_by = User.objects.filter(pk=logedin_user_id)[0]
        owner = User.objects.filter(username=owner_username)[0]
        question = QuestionModel(owner=owner,
                                 asked_by=asked_by,
                                 content=content)
        question.save()


class UnansweredView(FormView):
    pass
