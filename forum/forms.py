from django import forms

from forum.models import *

__all__ = ["ArticleForm", "CommentForm"]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ('author', "date_created")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
