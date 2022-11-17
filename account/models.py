from datetime import datetime

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.db.models.functions import Lower
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from account.managers import UserManager, FriendManager
from account.signals import friend_request_accepted, friend_request_rejected

__all__ = ["User", "Profile", "Friend", "FriendRequest"]


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(
        _("login"),
        max_length=32,
        unique=True,
        error_messages={
            "unique": _("A user with that login already exists."),
        },
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "login"



class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    email = models.EmailField(_('email address'), default='')
    username = models.CharField(_('username'), max_length=32, default='Stranger')
    balance = models.PositiveIntegerField(_('coin balance'), default=0)
    image = models.ImageField(_("profile image"), upload_to="img/", default="img/defaultProfile.jpg")
    about = models.TextField(_("About yourself"), default="I'm using SimpleForum")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_or_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

    else:
        try:
            instance.profile.save()

        except ObjectDoesNotExist:
            Profile.objects.create(user=instance)


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="friend_requests_from", on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="friend_requests_to", on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def finished(self):
        self.delete()

    def accept(self):
        friend_request_accepted.send(sender=self)
        self.finished()

    def reject(self):
        friend_request_rejected(sender=self)
        self.finished()


class Friend(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="friends_from", on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="friends_to", on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    objects = FriendManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('from_user'),
                Lower('to_user').desc(),
                name="pair of user's unique"
            ),
        ]


@receiver(friend_request_accepted, sender=FriendRequest)
def accept_friend(sender: FriendRequest, **kwargs) -> None:
    try:
        Friend.objects.create_friends(sender.from_user, sender.to_user)
    except ValidationError as e:
        print("ERROR:", e, "date time:", datetime.now())  # TODO: Change to normal log
