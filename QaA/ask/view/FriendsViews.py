
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic.base import View
from django.views.generic.edit import FormMixin

from ..forms import FriendAcceptedForm, FriendSearchForm
from ..models import FriendsModel
from .MixIns import *


class FriendsBase(View, QuestionsMixIn, FriendsMixIn):

    def get(self, request):
        try:
            user = UserModel.objects.get(
                pk=request.session['_auth_user_id'])
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        context = self.get_context(user, request)
        return render(request, "ask/friends.html", context=context)

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    @AvatarMinIn.add_avatar_to_context
    def get_context(self, user, request):
        friends = self.user_friends(user)
        context = {"friends": friends}
        return context


class FriendsRecent(FriendsBase):

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    @AvatarMinIn.add_avatar_to_context
    def get_context(self, user, request):
        friends = self.order_by_date(user)
        context = {"friends": friends}
        return context

    def order_by_date(self, user):
        date = [f.date for f in user.friendsmodel_set.all()]
        second_date = [f.date for f in user.friends_second.all()]
        friends_with_date = list(
            zip(self.user_friends(user), date + second_date))
        friends_with_date.sort(key=lambda t: t[1].time())
        friends = [t[0] for t in friends_with_date]
        return friends[::-1]


class FriendsAlphabetical(FriendsBase):

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    @AvatarMinIn.add_avatar_to_context
    def get_context(self, user, request):
        friends = self.order_by_alphabet(user)
        context = {"friends": friends}
        return context

    def order_by_alphabet(self, user):
        friends = self.user_friends(user)
        friends.sort(key=lambda f: f.username)
        return friends


class FriendsInvitationList(FriendsBase):

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    @AvatarMinIn.add_avatar_to_context
    def get_context(self, user, request):
        context = {
            'show_invites': True,
            'invitations': self.user_friends(user, accepted=False),
        }
        return context


class FriendAcceptedView(View, FormMixin):
    form_class = FriendAcceptedForm

    def post(self, request):
        form = self.get_form()

        if form.is_valid():
            self.find_users_and_accept(request.session['_auth_user_id'],
                                       form.cleaned_data['user_id'])

        return FriendsInvitationList().get(request)

    def find_users_and_accept(self, user1_id, user2_id):
        user_first = UserModel.objects.get(pk=user1_id)
        user_second = UserModel.objects.get(pk=user2_id)

        try:
            self.accept_invitation(user_second, user_first)
        except FriendsModel.DoesNotExist:
            self.accept_invitation(user_first, user_second)

    def accept_invitation(self, user1, user2):
        friends = FriendsModel.objects.get(first=user1, second=user2)
        friends.accepted = True
        friends.save()


class FriendSearchView(View, QuestionsMixIn, FriendsMixIn, FormMixin):
    form_class = FriendSearchForm

    def post(self, request):
        try:
            user = UserModel.objects.get(
                pk=request.session['_auth_user_id'])
        except KeyError:
            return HttpResponseRedirect(reverse('ask:login'))

        context = self.get_context(user, request)
        return render(request, "ask/friends.html", context=context)

    @QuestionsMixIn.add_num_unanswered_to_context
    @FriendsMixIn.add_num_invites_to_context
    @AvatarMinIn.add_avatar_to_context
    def get_context(self, user, request):
        form = self.get_form()
        context = {}
        if form.is_valid():
            searched_user = form.cleaned_data['search_text']
            context = {'friends': self.get_matching_friends(
                user, searched_user)}
        return context

    def get_matching_friends(self, user, searched_user):
        friends = self.user_friends(user)
        return [f for f in friends if searched_user in f.username]
