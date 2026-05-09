from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.TopicListView.as_view(), name="index"),
    path("posts/new/", views.TopicPartCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/edit/", views.TopicPartUpdateView.as_view(), name="post_edit"),
    path("topics/<slug:slug>/", views.TopicDetailView.as_view(), name="topic_detail"),
    path("topics/<slug:slug>/like/", views.topic_like_toggle, name="topic_like_toggle"),
    path(
        "topics/<slug:slug>/comments/<int:pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment_delete",
    ),
    path("posts/<int:pk>/", views.PostDetailRedirectView.as_view(), name="post_detail"),
]
