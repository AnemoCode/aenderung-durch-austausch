from django.urls import path

from . import views

app_name = 'topics'

urlpatterns = [
    path('', views.TopicListView.as_view(), name='topic_list'),
    path('<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('<int:topic_pk>/parts/new/', views.TopicPartCreateView.as_view(), name='topicpart_create'),
    path('parts/<int:pk>/edit/', views.TopicPartUpdateView.as_view(), name='topicpart_edit'),
]
