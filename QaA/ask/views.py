from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.base import View

from .models import QuestionModel, AnswerModel

from .forms import SignUpForm


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
    success_url = 'user'

    def form_valid(self, form):
        user = self.form_to_model(form)
        user.save()
        return super().form_valid(form)

    def form_to_model(self, form):
        clean_data = form.cleaned_data
        del clean_data['password_repeat']
        del clean_data['terms']
        del clean_data['privacy']
        return User(**clean_data)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            request.session['logged_in'] = True
            request.session['username'] = form.cleaned_data['username']
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class UserView(View):

    def get(self, request):
        if not self.is_user_logged_in(request.session):
            return HttpResponseRedirect("ask/login.html")
        context = self.get_context(request)
        return render(request, "ask/user.html", context=context)

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
        questions_with_answers = self.get_answered_questions_with_answers(
            user_id)
        num_unanswered = self.get_num_unanswered(user_id)
        context = {"questions_with_answers": questions_with_answers,
                   "num_unanswered": num_unanswered}
        return context

    def get_answered_questions_with_answers(self, user_id):
        user = User.objects.get(pk=user_id)
        answered_questions = QuestionModel.objects.filter(
            owner=user).exclude(answer=None).order_by('date')[::-1]
        answers = [question.answer for question in answered_questions]
        return list(zip(answered_questions, answers))

    def get_num_unanswered(self, user_id):
        user = User.objects.get(pk=user_id)
        unanswered_questions = QuestionModel.objects.filter(
            owner=user).filter(answer=None)
        return len(unanswered_questions)
