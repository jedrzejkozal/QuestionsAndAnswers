from django.urls import path
from django.contrib.auth.views import LoginView, TemplateView

from . import views

app_name = "ask"
urlpatterns = [
    path('', views.index, name='index'),
    path('login', LoginView.as_view(template_name='ask/login.html'), name='login'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('user', views.user_profile, name='user'),
    path('terms', TemplateView.as_view(
        template_name='ask/terms.html'), name='terms'),
    path('privacypolicy', TemplateView.as_view(
        template_name='ask/privacypolicy.html'), name='privacypolicy')
]
