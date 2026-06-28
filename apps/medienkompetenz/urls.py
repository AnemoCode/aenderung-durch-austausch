from django.urls import path

from . import views

app_name = 'medienkompetenz'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='index'),
    path('neu/', views.ArticleCreateView.as_view(), name='create'),
    path('uploads/image/', views.image_upload, name='image_upload'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),
    path('<slug:slug>/bearbeiten/', views.ArticleUpdateView.as_view(), name='edit'),
    path(
        '<slug:slug>/abschnitte/neu/<str:block_type>/',
        views.BlockCreateView.as_view(),
        name='block_create',
    ),
    path(
        '<slug:slug>/abschnitte/<int:pk>/bearbeiten/',
        views.BlockUpdateView.as_view(),
        name='block_edit',
    ),
    path(
        '<slug:slug>/abschnitte/<int:pk>/loeschen/',
        views.BlockDeleteView.as_view(),
        name='block_delete',
    ),
]
