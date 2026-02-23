from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext as _
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from ..forms import AddMemberForm, AddProjectToGroupForm, ProjectGroupForm
from ..models import GroupMembership, GroupProject, ProjectGroup


class GroupListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/groups.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return (
            ProjectGroup.objects
            .filter(members=self.request.user)
            .annotate(
                members_count=Count('members', distinct=True),
                projects_count=Count('projects', distinct=True),
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        for group in ctx['groups']:
            group.user_role = group.get_member_role(user)
        ctx['active_nav'] = 'groups'
        return ctx


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = ProjectGroup
    form_class = ProjectGroupForm
    template_name = 'dashboard/group_form.html'
    success_url = reverse_lazy('dashboard:groups')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        GroupMembership.objects.create(
            group=self.object,
            user=self.request.user,
            role=GroupMembership.Role.ADMIN,
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'groups'
        return ctx


class GroupMemberMixin(UserPassesTestMixin):
    """Restricts access to group members. Caches get_object() to avoid double queries."""

    def get_object(self, queryset=None):
        if not hasattr(self, '_object'):
            self._object = super().get_object(queryset)
        return self._object

    def test_func(self):
        return self.get_object().members.filter(pk=self.request.user.pk).exists()


class GroupAdminMixin(UserPassesTestMixin):
    """Restricts access to group admins. Caches get_object() to avoid double queries."""

    def get_object(self, queryset=None):
        if not hasattr(self, '_object'):
            self._object = super().get_object(queryset)
        return self._object

    def test_func(self):
        return self.get_object().is_admin(self.request.user)


class GroupDetailView(LoginRequiredMixin, GroupMemberMixin, DetailView):
    model = ProjectGroup
    template_name = 'dashboard/group_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        group = self.object
        user = self.request.user
        ctx.update({
            'active_nav': 'groups',
            'memberships': group.memberships.select_related('user'),
            'group_projects': group.group_projects.select_related('project__owner', 'added_by'),
            'user_role': group.get_member_role(user),
            'is_admin': group.is_admin(user),
            'add_member_form': AddMemberForm(group=group),
            'add_project_form': AddProjectToGroupForm(group=group, user=user),
        })
        return ctx


class GroupDeleteView(LoginRequiredMixin, GroupAdminMixin, DeleteView):
    model = ProjectGroup
    template_name = 'dashboard/group_confirm_delete.html'
    success_url = reverse_lazy('dashboard:groups')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'groups'
        return ctx


# ── Action views (POST-only, no template) ─────────────────────────────────────

class AddMemberView(LoginRequiredMixin, UserPassesTestMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.group = get_object_or_404(ProjectGroup, pk=kwargs['pk'])

    def test_func(self):
        return self.group.is_admin(self.request.user)

    def post(self, request, pk):
        form = AddMemberForm(group=self.group, data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['email']  # clean_email returns the User object
            GroupMembership.objects.create(group=self.group, user=user)
            messages.success(request, _('"{name}" wurde zur Gruppe hinzugefügt.').format(name=user.name))
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
        return redirect('dashboard:group_detail', pk=pk)


class RemoveMemberView(LoginRequiredMixin, UserPassesTestMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.group = get_object_or_404(ProjectGroup, pk=kwargs['pk'])

    def test_func(self):
        return self.group.is_admin(self.request.user)

    def post(self, request, pk, user_pk):
        membership = get_object_or_404(GroupMembership, group=self.group, user_id=user_pk)
        is_last_admin = (
            membership.role == GroupMembership.Role.ADMIN
            and self.group.memberships.filter(role=GroupMembership.Role.ADMIN).count() == 1
        )
        if is_last_admin:
            messages.error(request, _('Die Gruppe braucht mindestens einen Admin.'))
        else:
            name = membership.user.name
            membership.delete()
            messages.success(request, _('"{name}" wurde aus der Gruppe entfernt.').format(name=name))
        return redirect('dashboard:group_detail', pk=pk)


class AddProjectView(LoginRequiredMixin, UserPassesTestMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.group = get_object_or_404(ProjectGroup, pk=kwargs['pk'])

    def test_func(self):
        return self.group.members.filter(pk=self.request.user.pk).exists()

    def post(self, request, pk):
        form = AddProjectToGroupForm(group=self.group, user=request.user, data=request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            GroupProject.objects.create(group=self.group, project=project, added_by=request.user)
            messages.success(request, _('"{name}" wurde zur Gruppe hinzugefügt.').format(name=project.name))
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
        return redirect('dashboard:group_detail', pk=pk)


class RemoveProjectView(LoginRequiredMixin, UserPassesTestMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.group = get_object_or_404(ProjectGroup, pk=kwargs['pk'])
        self.group_project = get_object_or_404(
            GroupProject, group=self.group, project_id=kwargs['project_pk']
        )

    def test_func(self):
        return (
            self.group_project.project.owner == self.request.user
            or self.group.is_admin(self.request.user)
        )

    def post(self, request, pk, project_pk):
        project_name = self.group_project.project.name
        self.group_project.delete()
        messages.success(request, _('"{name}" wurde aus der Gruppe entfernt.').format(name=project_name))
        return redirect('dashboard:group_detail', pk=pk)
