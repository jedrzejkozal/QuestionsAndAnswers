from django.urls import path
from django.contrib.auth.views import TemplateView
from django.contrib.sitemaps.views import sitemap

from . import views
from .view import FriendsViews as friends
from .sitemaps import *


sitemaps = {
    'static': StaticViewSitemap,
}

app_name = "ask"
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.CustomLoginView.as_view(
        template_name='ask/login.html'), name='login'),
    path('logout', views.CustomLogoutView.as_view(
        template_name='ask/logout.html'), name='logout'),
    path('signup', views.SignUpView.as_view(), name='signup'),

    path('terms', TemplateView.as_view(
         template_name='ask/terms.html'), name='terms'),
    path('privacypolicy', TemplateView.as_view(
        template_name='ask/privacypolicy.html'), name='privacypolicy'),

    path('profile', views.ProfileView.as_view(), name='profile'),
    path('user/<str:username>', views.UserView.as_view(), name='user'),
    path('unanswered', views.UnansweredView.as_view(), name='unanswered'),

    path('friends/recent', friends.FriendsRecent.as_view(), name='friends.recent'),
    path('friends/alph', friends.FriendsAlphabetical.as_view(), name='friends.alph'),
    path('friends/inv', friends.FriendsInvitationList.as_view(), name='friends.inv'),
    path('friends/accept', friends.FriendAcceptedView.as_view(),
         name='friends.accept'),
    path('friends/search', friends.FriendSearchView.as_view(), name='friends.search'),
    path('friends', friends.FriendsBase.as_view(), name='friends'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemaps')
]
