import datetime
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Subquery, Sum
from django.utils.translation import gettext as _, ngettext
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
            .order_by('taken_at')
            .values('taken_at', 'word_count', 'page_count')
        )
        data = [
            {'x': r['taken_at'].isoformat(), 'words': r['word_count'], 'pages': r['page_count']}
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
            total_citations=Sum('citation_count'),
            total_floats=Sum('float_count'),
            total_math=Sum('math_count'),
        )

        week_ago = timezone.now() - datetime.timedelta(days=7)

        def _prev_sub(field):
            return Subquery(
                ProjectSnapshot.objects
                .filter(project=OuterRef('pk'), taken_at__lte=week_ago)
                .order_by('-taken_at').values(field)[:1]
            )

        baseline = projects.annotate(
            base_cit=_prev_sub('citation_count'),
            base_flt=_prev_sub('float_count'),
            base_mth=_prev_sub('math_count'),
        ).aggregate(
            base_citations=Sum('base_cit'),
            base_floats=Sum('base_flt'),
            base_math=Sum('base_mth'),
        )

        ctx.update({
            'active_nav': 'index',
            'projects': projects,
            'chart_data_json': self._build_chart_data(self.request.user),
            'stats': {
                'total_words':     totals['total_words']     or 0,
                'total_pages':     totals['total_pages']     or 0,
                'active_projects': projects.count(),
                'total_citations': totals['total_citations'] or 0,
                'total_floats':    totals['total_floats']    or 0,
                'total_math':      totals['total_math']      or 0,
                'citation_delta':  (totals['total_citations'] or 0) - (baseline['base_citations'] or 0),
                'float_delta':     (totals['total_floats']    or 0) - (baseline['base_floats']    or 0),
                'math_delta':      (totals['total_math']      or 0) - (baseline['base_math']      or 0),
            },
        })
        return ctx


class SyncAllView(LoginRequiredMixin, View):
    """Enqueue a sync for every project belonging to this user."""
    def post(self, request):
        if not request.user.overleaf_token:
            messages.error(
                request,
                _('Keine Projekte zum Synchronisieren gefunden. '
                  'Bitte hinterlege zuerst einen Overleaf-Token in den Einstellungen.'),
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
                ngettext(
                    'Synchronisation für %(count)d Projekt gestartet – '
                    'Ergebnisse erscheinen in wenigen Sekunden.',
                    'Synchronisation für %(count)d Projekte gestartet – '
                    'Ergebnisse erscheinen in wenigen Sekunden.',
                    count,
                ) % {'count': count},
            )
        else:
            messages.error(
                request,
                _('Keine Projekte zum Synchronisieren gefunden. '
                  'Bitte hinterlege zuerst einen Overleaf-Token in den Einstellungen.'),
            )
        return redirect('dashboard:index')


class SyncProjectView(LoginRequiredMixin, View):
    """Enqueue a sync for a single project owned by this user."""
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        if not request.user.overleaf_token:
            messages.error(
                request,
                _('Kein Overleaf-Token gespeichert. Bitte hinterlege ihn in den Einstellungen.'),
            )
            return redirect('dashboard:index')
        sync_project.delay(project.pk)
        messages.success(
            request,
            _('Synchronisation für „%(name)s" gestartet – '
              'Ergebnisse erscheinen in wenigen Sekunden.') % {'name': project.name},
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
                messages.success(request, _('Overleaf-Token wurde verschlüsselt gespeichert.'))
            else:
                messages.error(request, _('Bitte gib einen gültigen Token ein.'))

        elif action == 'delete_token':
            request.user.overleaf_token = None
            request.user.save(update_fields=['overleaf_token'])
            messages.success(request, _('Overleaf-Token wurde entfernt.'))

        return redirect('dashboard:settings')
