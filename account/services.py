from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest

from account.models import FriendRequest, Friend
from account.forms import UserCreationForm, FriendRequestForm

__all__ = ["auth_user", "register_user", "answer_friend_request",
           "delete_friend", "create_friend_request"]


def auth_user(username: str, password: str, request: HttpRequest) -> None:
    user = authenticate(username=username, password=password)

    if user is None:
        raise ValidationError(_("Incorrect login or password"))

    login(request, user)


def register_user(form: UserCreationForm, request: HttpRequest) -> None:
    user = form.save()
    login(request, user)


def answer_friend_request(request: HttpRequest, frid: int, answer: str):
    friend_request = get_object_or_404(FriendRequest, id=frid)

    if answer == "accept":
        if friend_request.to_user != request.user:
            raise PermissionDenied("Friend request can accept only aim user.")

        friend_request.accept()
    elif answer == "reject":
        if friend_request.to_user != request.user:
            raise PermissionDenied("Friend request can reject only aim user.")

        friend_request.reject()

    elif answer == "cancel":
        if friend_request.from_user != request.user:
            raise PermissionDenied("Friend request can cancel only author.")

        friend_request.finished()

    raise ValidationError("Bad answer")


def delete_friend(request, fid: int):
    friend_model = get_object_or_404(Friend, id=fid)
    if friend_model.from_user != request.user:
        raise PermissionDenied("Delete friend can only owner.")
    Friend.objects.delete_friends(friend_model.from_user, friend_model.to_user)


def create_friend_request(from_user, form: FriendRequestForm):
    if not form.is_valid():
        raise ValidationError(_("Form is invalid"))

    to_user = form.cleaned_data["to_user"]

    if Friend.objects.are_friends(from_user, to_user):
        raise ValidationError(_("You are already friends."))

    if FriendRequest.objects.filter(
            Q(from_user=from_user, to_user=to_user) |
            Q(from_user=to_user, to_user=from_user)).exists():
        raise ValidationError(_("You have a friend request."))

    friend_request = form.save(commit=False)
    friend_request.from_user = from_user
    friend_request.save()
