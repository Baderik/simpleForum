from django.contrib import admin

from forum.models import *


class CommentInline(admin.TabularInline):
    model = Comment


class CommentRatingInline(admin.TabularInline):
    model = LikeDislikeComment


class ArticleRatingInline(admin.TabularInline):
    model = LikeDislikeArticle


class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        ArticleRatingInline,
        CommentInline
    ]


class CommentAdmin(admin.ModelAdmin):
    inlines = [
        CommentRatingInline
    ]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(LikeDislikeArticle)
admin.site.register(LikeDislikeComment)
