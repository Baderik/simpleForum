from datetime import datetime

from django.contrib.auth import logout, get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest

from account.forms import UserLoginForm, UserCreationForm, ProfileForm, FriendRequestForm
from account.services import auth_user, register_user, answer_friend_request, delete_friend, create_friend_request
from account.models import Friend, FriendRequest, Profile

from django.views.generic import ListView

__all__ = ["LoginView", "CreationUserView", "LogoutView",
           "IndexProfileView", "PeopleListView", "ProfileView", "SettingsView",
           "FriendListView", "FriendView",
           "FriendRequestListView", "FriendRequestView", "IndexFriendRequestView"]


class LoginView(UserPassesTestMixin, View):
    login_url: str = "/"

    def test_func(self):
        return not self.request.user.is_authenticated

    @staticmethod
    def get(request: HttpRequest):
        return render(request, "account/auth.html", {"form": UserLoginForm})

    def post(self, request: HttpRequest):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            try:
                auth_user(
                    form.cleaned_data["login"],
                    form.cleaned_data["password"],
                    request)
                return redirect(self.login_url)

            except ValidationError as e:
                for el in e.messages:
                    form.add_error(None, el)

        return render(request, "account/auth.html",
                      {"form": form})


class CreationUserView(UserPassesTestMixin, View):
    login_url: str = "/"

    def test_func(self):
        return not self.request.user.is_authenticated

    @staticmethod
    def get(request: HttpRequest):
        return render(request, "account/auth.html", {"form": UserCreationForm})

    def post(self, request: HttpRequest):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            register_user(form, request)
            return redirect(self.login_url)

        return render(request, "account/auth.html", {"form": form})


class LogoutView(View):
    @staticmethod
    def get(request: HttpRequest):
        logout(request)

        return redirect(resolve_url("index"))


class IndexProfileView(View):
    @staticmethod
    def get(request: HttpRequest):
        return redirect(resolve_url("article-list"))


class ProfileView(View):
    @staticmethod
    def get(request: HttpRequest, uid: int):
        user = get_object_or_404(get_user_model(), id=uid)

        return render(request, "account/profile.html", {
            "user": request.user,
            "owner": user.profile,
            "articles": user.article_set.order_by("-created_at"),
            "is_owner": request.user.id == user.id,
            "friend": Friend.objects.filter(from_user=request.user, to_user=user).first(),
            "sent_friend_request": FriendRequest.objects.filter(from_user=request.user, to_user=user).first(),
            "have_friend_request": FriendRequest.objects.filter(from_user=user, to_user=request.user).first(),
            "fr_form": FriendRequestForm(),
        })

    @staticmethod
    def post(request: HttpRequest, uid: int):
        if uid != request.user.id:
            raise PermissionError("Only owner can change settings.")

        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            form.save()

            return redirect(resolve_url("user-settings"))

        return render(request, "account/settings.html",
                      {"user": request.user,
                       "form": form})


class SettingsView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        return render(request, "account/settings.html",
                      {"user": request.user,
                       "form": ProfileForm(instance=request.user.profile),
                       "change_search": resolve_url("article-list")})


class FriendListView(LoginRequiredMixin, ListView):
    model = Friend
    paginate_by = 5
    template_name = 'account/friends.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(FriendListView, self).get_context_data(**kwargs)
        ctx["change_search"] = resolve_url("article-list")
        return ctx

    def get_queryset(self):
        return Friend.objects.filter(from_user=self.request.user).order_by("-created_at")


class FriendView(View):
    @staticmethod
    def get():
        return redirect(resolve_url("friend-list"))

    def post(self, request: HttpRequest, fid: int):
        return self.delete(request, fid)

    @staticmethod
    def delete(request: HttpRequest, fid: int):
        try:
            delete_friend(request, fid)
        except PermissionError as e:
            print("ERROR:", e, "date time:", datetime.now())

        return redirect(resolve_url("friend-list"))


class PeopleListView(ListView):
    model = Profile
    paginate_by = 5
    template_name = 'account/people.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(PeopleListView, self).get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get("q", "")
        return ctx

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        return Profile.objects.filter(username__contains=query).order_by("-username")


class IndexFriendRequestView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        return redirect("out/")

    @staticmethod
    def post(request):
        form = FriendRequestForm(request.POST)
        try:
            create_friend_request(request.user, form)
        except ValidationError as e:
            print("ERROR:", e, "date time:", datetime.now())  # TODO: Change to normal log
            return redirect(resolve_url("index"))
        return redirect(resolve_url("profile-detail", uid=form.cleaned_data["to_user"].id))


class FriendRequestListView(LoginRequiredMixin, ListView):
    model = FriendRequest
    paginate_by = 5
    template_name = 'account/friendRequests.html'
    request_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(FriendRequestListView, self).get_context_data(**kwargs)
        ctx['change_search'] = '?'
        ctx['query'] = self.request.GET.get("q", "")
        ctx["request_type"] = self.request_type
        return ctx

    def get_queryset(self):
        if self.request_type == "from":
            return FriendRequest.objects.filter(from_user=self.request.user).order_by("-created_at")
        else:
            return FriendRequest.objects.filter(to_user=self.request.user).order_by("-created_at")


class FriendRequestView(View):
    @staticmethod
    def get():
        return redirect(resolve_url("friend-request-list"))

    @staticmethod
    def post(request, frid: int, result: str):
        try:
            answer_friend_request(request, frid, result)
        except PermissionError as e:
            print("ERROR:", e, "date time:", datetime.now())  # TODO: Change to normal log

        except ValidationError as e:
            print("ERROR:", e, "date time:", datetime.now())  # TODO: Change to normal log

        return redirect(resolve_url("friend-request-list"))
