from django.conf import settings
from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        OK = 'OK', 'Aktiv'
        AUTH_ERROR = 'AUTH_ERROR', 'Auth Error'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
    )
    name = models.CharField(max_length=255)
    git_url = models.URLField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OK)
    word_count = models.PositiveIntegerField(default=0)
    page_count = models.PositiveIntegerField(default=0)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProjectGroup(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMembership',
        related_name='project_groups',
    )
    projects = models.ManyToManyField(
        Project,
        through='GroupProject',
        related_name='groups',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Gruppe'
        verbose_name_plural = 'Gruppen'

    def __str__(self):
        return self.name

    def get_member_role(self, user):
        try:
            return self.memberships.get(user=user).role
        except GroupMembership.DoesNotExist:
            return None

    def is_admin(self, user):
        return self.get_member_role(user) == GroupMembership.Role.ADMIN


class GroupMembership(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Mitglied'

    group = models.ForeignKey(
        ProjectGroup,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships',
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')
        ordering = ['joined_at']

    def __str__(self):
        return f'{self.user} in {self.group} ({self.get_role_display()})'


class GroupProject(models.Model):
    group = models.ForeignKey(
        ProjectGroup,
        on_delete=models.CASCADE,
        related_name='group_projects',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='group_projects',
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_group_projects',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'project')
        ordering = ['added_at']

    def __str__(self):
        return f'{self.project} in {self.group}'
