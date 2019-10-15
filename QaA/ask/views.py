from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.views.generic.edit import FormView

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


def user_profile(request):
    return render(request, "ask/user.html")


def logout(request):
    pass
