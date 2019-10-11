from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    # return HttpResponse("This is main page")
    return render(request, "ask/index.html")
