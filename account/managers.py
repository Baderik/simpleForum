from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

__all__ = ["UserManager", "FriendManager"]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, login: str, password: str, **extra_fields):
        if not login:
            raise ValueError('The given login must be set')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, login=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(login, password, **extra_fields)

    def create_superuser(self, login, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(login, password, **extra_fields)


class FriendManager(models.Manager):
    def _are_friends(self, user_1, user_2) -> bool:
        return self.filter(
            Q(from_user=user_1, to_user=user_2) |
            Q(from_user=user_2, to_user=user_1)).exists()

    def are_friends(self, user_1, user_2) -> bool:
        if user_1 == user_2:
            raise ValidationError("Users cannot be friends with themselves.")

        return self._are_friends(user_1, user_2)

    def _create_by_users(self, from_user, to_user):
        friend = self.model(from_user=from_user, to_user=to_user).save()

        return friend

    def create_friends(self, user_1, user_2):
        if user_1 == user_2:
            raise ValidationError("Users cannot be friends with themselves.")
        if self._are_friends(user_1, user_2):
            raise ValidationError("Users are already friends.")

        self._create_by_users(user_1, user_2)
        self._create_by_users(user_2, user_1)

    def delete_friends(self, user_1, user_2):
        friends = self.filter(
            Q(from_user=user_1, to_user=user_2) |
            Q(from_user=user_2, to_user=user_1))

        if not friends.exists():
            raise ValidationError("Users are not friends.")

        friends.delete()
