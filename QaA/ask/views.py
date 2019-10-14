from django.contrib.auth.models import User
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.views.generic.edit import FormView

from .forms import SignUpForm


def index(request):
    return render(request, "ask/index.html")


class SignUpView(FormView):
    template_name = 'ask/signup.html'
    form_class = SignUpForm
    success_url = 'ask/user'

    def form_valid(self, form):
        user = self.form_to_model(form)
        user.save()
        return super().form_valid(form)

    def form_to_model(self, form):
        clean_data = form.cleaned_data
        del clean_data['password_repeat']
        return User(**clean_data)


def user_profile(request):
    return render(request, "ask/user.html")
