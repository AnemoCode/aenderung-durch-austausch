import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Max, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView

from ..models import Project, ProjectGroup, ProjectSnapshot

User = get_user_model()


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True
    http_method_names = ['get', 'head', 'options']

    def test_func(self):
        return self.request.user.is_staff


class StaffOverviewView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/staff/overview.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        totals = Project.objects.aggregate(
            total_words=Sum('word_count'),
            total_pages=Sum('page_count'),
            total_projects=Count('id'),
        )
        snapshot_count = ProjectSnapshot.objects.count()
        group_count = ProjectGroup.objects.count()
        user_count = User.objects.filter(is_active=True).count()
        staff_count = User.objects.filter(is_staff=True, is_active=True).count()
        users_with_token = User.objects.filter(
            is_active=True, overleaf_token__isnull=False
        ).exclude(overleaf_token='').count()

        recent_users = (
            User.objects
            .filter(is_active=True)
            .order_by('-date_joined')[:5]
        )
        recent_syncs = (
            Project.objects
            .filter(last_synced_at__isnull=False)
            .select_related('owner')
            .order_by('-last_synced_at')[:5]
        )

        ctx.update({
            'active_nav': 'staff',
            'stats': {
                'user_count': user_count,
                'staff_count': staff_count,
                'users_with_token': users_with_token,
                'total_projects': totals['total_projects'] or 0,
                'total_words': totals['total_words'] or 0,
                'total_pages': totals['total_pages'] or 0,
                'snapshot_count': snapshot_count,
                'group_count': group_count,
            },
            'recent_users': recent_users,
            'recent_syncs': recent_syncs,
        })
        return ctx


class StaffUserListView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/staff/user_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        users = (
            User.objects
            .filter(is_active=True)
            .annotate(
                project_count=Count('projects', distinct=True),
                total_words=Sum('projects__word_count'),
                last_sync=Max('projects__last_synced_at'),
            )
            .order_by('date_joined')
        )

        ctx.update({
            'active_nav': 'staff',
            'users': users,
        })
        return ctx


class StaffUserDetailView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/staff/user_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        viewed_user = get_object_or_404(User, pk=self.kwargs['pk'])
        projects = (
            Project.objects
            .filter(owner=viewed_user)
            .prefetch_related('groups')
            .order_by('-last_synced_at')
        )
        cutoff = timezone.now() - datetime.timedelta(days=7)
        snapshots = (
            ProjectSnapshot.objects
            .filter(project__owner=viewed_user, taken_at__gte=cutoff)
            .select_related('project')
            .order_by('-taken_at')[:50]
        )

        ctx.update({
            'active_nav': 'staff',
            'viewed_user': viewed_user,
            'has_token': bool(viewed_user.overleaf_token),
            'projects': projects,
            'snapshots': snapshots,
        })
        return ctx
