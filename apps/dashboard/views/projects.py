from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from ..forms import ProjectForm
from ..models import Project


class ProjectListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return (
            Project.objects
            .filter(owner=self.request.user)
            .prefetch_related('groups')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'projects'
        return ctx


class ProjectOwnerMixin(UserPassesTestMixin):
    """Restricts access to the project owner. Caches get_object() to avoid double queries."""

    def get_object(self, queryset=None):
        if not hasattr(self, '_object'):
            self._object = super().get_object(queryset)
        return self._object

    def test_func(self):
        return self.get_object().owner == self.request.user


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dashboard/project_form.html'
    success_url = reverse_lazy('dashboard:projects')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'active_nav': 'projects', 'page_title': 'Neues Projekt'})
        return ctx


class ProjectUpdateView(LoginRequiredMixin, ProjectOwnerMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dashboard/project_form.html'
    success_url = reverse_lazy('dashboard:projects')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'active_nav': 'projects', 'page_title': 'Projekt bearbeiten'})
        return ctx


class ProjectDeleteView(LoginRequiredMixin, ProjectOwnerMixin, DeleteView):
    model = Project
    template_name = 'dashboard/project_confirm_delete.html'
    success_url = reverse_lazy('dashboard:projects')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'projects'
        return ctx
