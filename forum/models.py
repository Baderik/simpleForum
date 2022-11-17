from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from forum.managers import LikeDislikeManager

__all__ = ["Article", "Comment", "LikeDislikeArticle", "LikeDislikeComment"]


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    content = models.TextField(_("content of article"), default="")

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField(_("text of comment"))

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)


class LikeDislike(models.Model):
    LIKE, UNSET, DISLIKE = 1, 0, -1
    VOICES = (
        (LIKE, "Like"),
        (UNSET, "Unset"),
        (DISLIKE, "Dislike")
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote = models.SmallIntegerField(_("vote status"), choices=VOICES, default=0)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    objects = LikeDislikeManager()

    class Meta:
        abstract = True


class LikeDislikeArticle(LikeDislike):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class LikeDislikeComment(LikeDislike):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
