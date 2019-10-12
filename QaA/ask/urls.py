from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

app_name = "ask"
urlpatterns = [
    path('', views.index, name='index'),
    path('login', LoginView.as_view(template_name='ask/login.html'), name='login'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('user', views.user_profile, name='user')
]
