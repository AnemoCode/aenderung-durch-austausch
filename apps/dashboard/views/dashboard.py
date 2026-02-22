import datetime
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from ..models import Project, ProjectSnapshot
from ..tasks import sync_project


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    @staticmethod
    def _build_chart_data(user) -> str:
        cutoff = timezone.now() - datetime.timedelta(days=30)
        rows = (
            ProjectSnapshot.objects
            .filter(project__owner=user, taken_at__gte=cutoff)
            .annotate(date=TruncDate('taken_at'))
            .values('date')
            .annotate(words=Sum('word_count'), pages=Sum('page_count'))
            .order_by('date')
        )
        data = [
            {'date': r['date'].strftime('%Y-%m-%d'), 'words': r['words'], 'pages': r['pages']}
            for r in rows
        ]
        return json.dumps(data) if data else '[]'

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
            'chart_data_json': self._build_chart_data(self.request.user),
            'stats': {
                'total_words': totals['total_words'] or 0,
                'total_pages': totals['total_pages'] or 0,
                'active_projects': projects.count(),
            },
        })
        return ctx


class SyncAllView(LoginRequiredMixin, View):
    """Enqueue a sync for every project belonging to this user."""
    def post(self, request):
        if not request.user.overleaf_token:
            messages.error(
                request,
                'Keine Projekte zum Synchronisieren gefunden. '
                'Bitte hinterlege zuerst einen Overleaf-Token in den Einstellungen.',
            )
            return redirect('dashboard:index')
        projects = Project.objects.filter(owner=request.user)
        count = 0
        for p in projects:
            sync_project.delay(p.pk)
            count += 1
        if count:
            messages.success(
                request,
                f'Synchronisation für {count} Projekt{"e" if count != 1 else ""} gestartet – '
                'Ergebnisse erscheinen in wenigen Sekunden.',
            )
        else:
            messages.error(
                request,
                'Keine Projekte zum Synchronisieren gefunden. '
                'Bitte hinterlege zuerst einen Overleaf-Token in den Einstellungen.',
            )
        return redirect('dashboard:index')


class SyncProjectView(LoginRequiredMixin, View):
    """Enqueue a sync for a single project owned by this user."""
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        if not request.user.overleaf_token:
            messages.error(
                request,
                'Kein Overleaf-Token gespeichert. Bitte hinterlege ihn in den Einstellungen.',
            )
            return redirect('dashboard:index')
        sync_project.delay(project.pk)
        messages.success(
            request,
            f'Synchronisation für „{project.name}" gestartet – '
            'Ergebnisse erscheinen in wenigen Sekunden.',
        )
        return redirect('dashboard:index')


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
