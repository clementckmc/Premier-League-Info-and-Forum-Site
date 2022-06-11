from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("teams/<str:tla>", views.teamInfo, name="teamInfo"),
    path("table", views.table, name="table"),
    path("fixtures/<str:matchday>", views.fixtures, name="fixtures"),
    path("forum", views.forum, name="forum"),
    path("forum/<str:tla>", views.teamForum, name="teamForum"),
    path("forum/<str:tla>/new_thread", views.newPost, name="newPost"),
    path("thread/<slug:slug>", views.thread, name="thread"),
    path("vote_post/", views.vote_post, name="vote_post")
]