from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.views import View
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


class SettingsView(LoginRequiredMixin, View):
    template_name = 'dashboard/settings.html'

    def _context(self, request):
        token = request.user.overleaf_token
        masked = f'{"•" * 20}{token[-4:]}' if token and len(token) >= 4 else None
        return {
            'active_nav': 'settings',
            'has_token': bool(token),
            'masked_token': masked,
        }

    def get(self, request):
        return render(request, self.template_name, self._context(request))

    def post(self, request):
        action = request.POST.get('action')

        if action == 'save_token':
            token = request.POST.get('overleaf_token', '').strip()
            if token:
                request.user.overleaf_token = token
                request.user.save(update_fields=['overleaf_token'])
                messages.success(request, 'Overleaf-Token wurde verschlüsselt gespeichert.')
            else:
                messages.error(request, 'Bitte gib einen gültigen Token ein.')

        elif action == 'delete_token':
            request.user.overleaf_token = None
            request.user.save(update_fields=['overleaf_token'])
            messages.success(request, 'Overleaf-Token wurde entfernt.')

        return redirect('dashboard:settings')
