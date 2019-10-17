from django.urls import path
from django.contrib.auth.views import TemplateView

from . import views

app_name = "ask"
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.CustomLoginView.as_view(
        template_name='ask/login.html'), name='login'),
    path('logout', views.CustomLogoutView.as_view(
        template_name='ask/logout.html'), name='logout'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('user/<str:username>', views.UserView.as_view(), name='user'),
    path('terms', TemplateView.as_view(
        template_name='ask/terms.html'), name='terms'),
    path('privacypolicy', TemplateView.as_view(
        template_name='ask/privacypolicy.html'), name='privacypolicy'),
]
