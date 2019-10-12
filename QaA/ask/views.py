from django.shortcuts import render
from django.http.response import HttpResponseBadRequest

from .forms import SignUpForm


def index(request):
    return render(request, "ask/index.html")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            return render(request, "ask/user.html", status=200)
        else:
            return render(request, "ask/signup.html",
                          context={
                              'error_message': "Username must be specified"},
                          status=400)
    return render(request, "ask/signup.html", status=200)


def user_profile(request):
    return render(request, "ask/user.html")
