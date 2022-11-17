from django.contrib import admin

from account.models import User, Profile, Friend, FriendRequest


class ProfileInline(admin.TabularInline):
    model = Profile


class FriendInline(admin.TabularInline):
    model = Friend
    fk_name = "from_user"


class FriendRequestInline(admin.TabularInline):
    model = FriendRequest
    fk_name = "from_user"


class UserAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline,
        FriendInline,
        FriendRequestInline
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Friend)
admin.site.register(FriendRequest)
