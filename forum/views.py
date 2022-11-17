from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.views import View
from django.views.generic import ListView

from forum.forms import ArticleForm, CommentForm
from forum.services import *


__all__ = ["IndexView", "ArticleListView",
           "ArticleView", "CreateArticleView", "UpdateArticleView",
           "ArticleRatingView",
           "CommentView", "CommentRatingView"]


class IndexView(View):
    @staticmethod
    def get(request):
        return redirect(resolve_url("article-list"))


class ArticleListView(ListView):
    model = Article
    paginate_by = 5
    template_name = 'forum/index.html'

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        return Article.objects.filter(title__contains=query).order_by("-created_at")

    @staticmethod
    def post(request: HttpRequest):
        if not request.user.is_authenticated:
            return redirect(resolve_url("user-login"))
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = save_article(form, request.user)

            return redirect(resolve_url("article-detail", aid=article.id))

        return render(request, "forum/newArticle.html",
                      {"user": request.user,
                       "form": form,
                       "edit": True})


class ArticleView(View):
    my_method = None

    @staticmethod
    def get(request: HttpRequest, aid: int):
        article = get_object_or_404(Article, id=aid)

        return render(request, "forum/article.html",
                      {"user": request.user,
                       "article": article,
                       "comments": article.comment_set.order_by("-created_at"),
                       "form": CommentForm()})

    def post(self, request: HttpRequest, aid: int):  # Лень писать js код
        if self.my_method == "put":
            return self.put(request, aid)
        return self.delete(request, aid)

    @staticmethod
    def put(request: HttpRequest, aid: int):
        article = get_object_or_404(Article, id=aid)

        if not request.user.is_authenticated or \
                not request.user.is_active or \
                request.user.id != article.author.id:
            redirect(resolve_url("article-list"))

        form = ArticleForm(request.POST, instance=article)

        if not form.is_valid():
            return render(request, "forum/newArticle.html",
                          {"user": request.user,
                           "form": form})

        new_post = form.save(commit=False)
        new_post.save()

        return redirect(resolve_url("article-detail", aid=aid))

    @staticmethod
    def delete(request: HttpRequest, aid: int):
        article = get_object_or_404(Article, pk=aid)

        if request.user.is_authenticated and \
                article.author.id == request.user.id:
            article.delete()

        return redirect(resolve_url("article-list"))


class CreateArticleView(LoginRequiredMixin, View):
    @staticmethod
    def get(request: HttpRequest):
        return render(request, "forum/newArticle.html",
                      {"user": request.user,
                       "form": ArticleForm()})


class UpdateArticleView(LoginRequiredMixin, View):
    @staticmethod
    def get(request: HttpRequest, aid: int):
        article = get_object_or_404(Article, id=aid)

        if request.user.id != article.author.id:
            redirect(resolve_url("main-page"))

        return render(request, "forum/newArticle.html",
                      {"user": request.user,
                       "form": ArticleForm(instance=article),
                       "edit": True})


class ArticleRatingView(LoginRequiredMixin, View):
    vote_type = None

    @staticmethod
    def get(request: HttpRequest, aid: int):
        return redirect(resolve_url("article-detail", aid=aid))

    def post(self, request: HttpRequest, aid: int):
        article = get_object_or_404(Article, id=aid)
        article.likedislikearticle_set.set_votes_or_create(
            request.user, self.vote_type, article=article)
        return redirect(resolve_url("article-detail", aid=aid))


class CommentView(LoginRequiredMixin, View):
    @staticmethod
    def get(request: HttpRequest, aid: int):
        return redirect(resolve_url("article-detail", aid=aid))

    @staticmethod
    def post(request: HttpRequest, aid: int):
        article = get_object_or_404(Article, id=aid)

        form = CommentForm(request.POST)
        if form.is_valid():
            save_comment(form, article, request)

        return redirect(resolve_url("article-detail", aid=aid))


class CommentRatingView(LoginRequiredMixin, View):
    vote_type = None

    @staticmethod
    def get(request: HttpRequest, aid: int, cid: int):
        return redirect(resolve_url("article-detail", aid=aid))

    def post(self, request: HttpRequest, aid: int, cid: int):
        comment = get_object_or_404(Comment, id=cid)
        comment.likedislikecomment_set.set_votes_or_create(
            request.user, self.vote_type, comment=comment)
        return redirect(resolve_url("article-detail", aid=aid))
