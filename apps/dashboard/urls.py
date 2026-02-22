from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.projects, name='projects'),
    path('groups/', views.groups, name='groups'),
    path('settings/', views.settings_view, name='settings'),
]
