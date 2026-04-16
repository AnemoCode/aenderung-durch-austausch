from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.TopicListView.as_view(), name='index'),
    path('topics/<slug:slug>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('topics/<slug:slug>/like/', views.topic_like_toggle, name='topic_like_toggle'),
    path('posts/<int:pk>/', views.PostDetailRedirectView.as_view(), name='post_detail'),
]
