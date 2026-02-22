from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import TemplateView

from ..models import Project


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        projects = (
            Project.objects
            .filter(owner=self.request.user)
            .prefetch_related('groups')
        )
        totals = projects.aggregate(
            total_words=Sum('word_count'),
            total_pages=Sum('page_count'),
        )
        ctx.update({
            'active_nav': 'index',
            'projects': projects,
            'chart_data_json': '[]',
            'stats': {
                'total_words': totals['total_words'] or 0,
                'total_pages': totals['total_pages'] or 0,
                'active_projects': projects.count(),
            },
        })
        return ctx


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/settings.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'settings'
        return ctx
