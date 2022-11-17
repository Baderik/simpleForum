from django.urls import path
from forum.views import *
from forum.models import LikeDislikeArticle, LikeDislikeComment

urlpatterns = [
    path("", IndexView.as_view(), name="index"),

    path("article/", ArticleListView.as_view(), name="article-list"),
    path("article/<int:aid>/", ArticleView.as_view(), name="article-detail"),
    path("article/new/", CreateArticleView.as_view(), name="article-new"),
    path("article/<int:aid>/edit/", UpdateArticleView.as_view(), name="article-edit"),
    path("article/<int:aid>/put/", ArticleView.as_view(my_method='put'), name="article-update"),
    path("article/<int:aid>/delete/",
         ArticleView.as_view(my_method='delete'), name="article-delete"),

    path("article/<int:aid>/like/",
         ArticleRatingView.as_view(vote_type=LikeDislikeArticle.LIKE), name="article-like"),
    path("article/<int:aid>/dislike/",
         ArticleRatingView.as_view(vote_type=LikeDislikeArticle.DISLIKE), name="article-dislike"),

    path("article/<int:aid>/comment/", CommentView.as_view(), name="comment-detail"),
    path("article/<int:aid>/comment/<int:cid>/like/",
         CommentRatingView.as_view(vote_type=LikeDislikeComment.LIKE), name="comment-like"),
    path("article/<int:aid>/comment/<int:cid>/dislike/",
         CommentRatingView.as_view(vote_type=LikeDislikeComment.DISLIKE), name="comment-dislike")
]
