from django.conf import settings
from django.http import Http404, HttpRequest
from django.core.exceptions import PermissionDenied

from forum.models import Article, Comment


def filter_articles(query: str, page: int, count: int = 5):
    articles = Article.objects.filter(title__icontains=query)
    articles = articles.order_by("-created_at")

    next_article: bool = False
    last_article = (page - 1) * count
    if articles.count() > count + last_article:
        articles = articles[last_article:count + last_article]
        next_article: bool = True

    elif articles.count() > last_article:
        articles = articles[last_article:]

    elif articles.count():
        raise Http404

    return articles, last_article, next_article


def user_vote(article: Article, user: settings.AUTH_USER_MODEL) -> int:
    vote = article.likedislikearticle_set.filter(author=user)
    if vote.exists():
        return vote.first().vote
    else:
        return 0


def save_article(form, author):
    article: Article = form.save(commit=False)
    article.author = author
    article.save()

    return article


def save_comment(form, article, request):
    if not request.user.is_authenticated:
        return PermissionDenied("Only an authenticated user can create an comment.")

    comment = form.save(commit=False)
    comment.author = request.user
    comment.article = article
    comment.save()
    form.save_m2m()

    return comment


def delete_article(article: Article, request: HttpRequest):
    if not request.user.is_authenticated:
        return PermissionDenied("Only an authenticated user can create an article.")
    if request.user.id != article.author.id:
        return PermissionDenied("Only the author can delete an article.")

    article.delete()


def delete_comment(comment: Comment, request: HttpRequest):
    if not request.user.is_authenticated:
        return PermissionDenied("Only an authenticated user can create an comment.")
    if request.user.id != comment.author.id:
        return PermissionDenied("Only the author can delete an comment.")

    comment.delete()
