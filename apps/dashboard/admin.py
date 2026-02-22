from django.contrib import admin

from .models import GroupMembership, GroupProject, Project, ProjectGroup, ProjectSnapshot


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'word_count', 'page_count', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'owner__email', 'owner__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectGroup)
class ProjectGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'member_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

    @admin.display(description='Mitglieder')
    def member_count(self, obj):
        return obj.members.count()


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'user', 'role', 'joined_at']
    list_filter = ['role']


@admin.register(GroupProject)
class GroupProjectAdmin(admin.ModelAdmin):
    list_display = ['group', 'project', 'added_by', 'added_at']
    readonly_fields = ['added_at']


@admin.register(ProjectSnapshot)
class ProjectSnapshotAdmin(admin.ModelAdmin):
    list_display    = ['project', 'word_count', 'page_count', 'taken_at']
    list_filter     = ['project']
    readonly_fields = ['project', 'word_count', 'page_count', 'taken_at']
    ordering        = ['-taken_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
