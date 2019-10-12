from django.shortcuts import render
from django.http.response import HttpResponseBadRequest
from django.views.generic.edit import FormView

from .forms import SignUpForm


def index(request):
    return render(request, "ask/index.html")


class SignUpView(FormView):
    template_name = 'ask/signup.html'
    form_class = SignUpForm
    success_url = 'ask/user.html'

    def form_valid(self, form):
        # do something
        return super().form_valid(form)


def user_profile(request):
    return render(request, "ask/user.html")
