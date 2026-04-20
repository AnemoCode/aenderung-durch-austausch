from django.urls import path

from . import views

app_name = 'definitions'

urlpatterns = [
    path('', views.DefinitionListView.as_view(), name='index'),
    path('neu/', views.DefinitionCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.DefinitionDetailView.as_view(), name='detail'),
    path('<slug:slug>/bearbeiten/', views.DefinitionUpdateView.as_view(), name='edit'),
]
