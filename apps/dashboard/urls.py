from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    # Overview
    path('', views.DashboardView.as_view(), name='index'),
    path('settings/', views.SettingsView.as_view(), name='settings'),

    # Projects
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('projects/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # Groups
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path('groups/new/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),
    path('groups/<int:pk>/members/add/', views.AddMemberView.as_view(), name='group_add_member'),
    path('groups/<int:pk>/members/<int:user_pk>/remove/', views.RemoveMemberView.as_view(), name='group_remove_member'),
    path('groups/<int:pk>/projects/add/', views.AddProjectView.as_view(), name='group_add_project'),
    path('groups/<int:pk>/projects/<int:project_pk>/remove/', views.RemoveProjectView.as_view(), name='group_remove_project'),
]
