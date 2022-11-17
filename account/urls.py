from django.urls import path
from account.views import *

urlpatterns = [
    path("login/", LoginView.as_view(), name="user-login"),
    path("new/", CreationUserView.as_view(), name="user-register"),
    path("logout/", LogoutView.as_view(), name="user-logout"),

    path("", PeopleListView.as_view(), name="profile-list"),
    path("<int:uid>/", ProfileView.as_view(), name="profile-detail"),
    path("settings/", SettingsView.as_view(), name="profile-settings"),

    path("friend/", FriendListView.as_view(), name="friend-list"),
    path("friend/<int:fid>/delete/", FriendView.as_view(), name="friend-delete"),
    path("friend.request/", IndexFriendRequestView.as_view(), name="friend-request-index"),
    path("friend.request/out/",
         FriendRequestListView.as_view(request_type="from"), name="friend-request-out-list"),
    path("friend.request/in/",
         FriendRequestListView.as_view(request_type="to"), name="friend-request-in-list"),
    path("friend.request/<int:frid>/<str:result>/",
         FriendRequestView.as_view(), name="friend-request-list"),
]

