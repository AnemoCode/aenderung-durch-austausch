"""
Management command: seed_dev_data

Creates a reproducible set of development fixtures:
  - 1 demo user  (dev@overlytics.local / dev)
  - 3 projects   (thesis, paper, seminar work — each with a different trajectory)
  - 35 daily snapshots per project  (populates the 30-day chart + 7-day delta)
  - 1 group      (containing the first two projects)

Usage:
  python manage.py seed_dev_data           # create (idempotent)
  python manage.py seed_dev_data --flush   # wipe seed data first, then recreate
"""

import math
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.dashboard.models import GroupMembership, GroupProject, Project, ProjectGroup, ProjectSnapshot

User = get_user_model()

# ── Seed identity ──────────────────────────────────────────────────────────────
_DEV_EMAIL    = 'dev@overlytics.local'
_DEV_PASSWORD = 'dev'
_DEV_NAME     = 'Dev User'

# ── Project blueprints ────────────────────────────────────────────────────────
#  Each entry: (name, git_url, words_start, words_end, citations, floats, math, days_back)
#  days_back controls how many daily snapshots to generate (≤ 35).
_PROJECTS = [
    (
        'Masterarbeit Informatik',
        'https://git.overleaf.com/000000000000000000000001',
        18_500, 46_200,
        112, 24, 87,
        35,
    ),
    (
        'ICML 2026 Submission',
        'https://git.overleaf.com/000000000000000000000002',
        4_800, 8_100,
        54, 9, 41,
        35,
    ),
    (
        'Proseminar Komplexitätstheorie',
        'https://git.overleaf.com/000000000000000000000003',
        0, 3_900,
        18, 3, 12,
        12,          # started more recently → fewer snapshots
    ),
]

_GROUP_NAME = 'AG Schreiben'


class Command(BaseCommand):
    help = 'Seed the database with dummy development data (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing seed data before recreating it.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        user  = self._get_or_create_user()
        projs = [self._seed_project(user, bp) for bp in _PROJECTS]
        self._seed_group(user, projs[:2])   # thesis + paper share a group

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed complete — log in as  {_DEV_EMAIL}  /  {_DEV_PASSWORD}\n'
        ))

    # ── helpers ────────────────────────────────────────────────────────────────

    def _flush(self):
        try:
            u = User.objects.get(email=_DEV_EMAIL)
            count, _ = Project.objects.filter(owner=u).delete()
            ProjectGroup.objects.filter(created_by=u).delete()
            u.delete()
            self.stdout.write(f'  Flushed seed user and {count} project(s).')
        except User.DoesNotExist:
            self.stdout.write('  Nothing to flush.')

    def _get_or_create_user(self):
        user, created = User.objects.get_or_create(
            email=_DEV_EMAIL,
            defaults={'name': _DEV_NAME},
        )
        if created:
            user.set_password(_DEV_PASSWORD)
            user.save(update_fields=['password'])
            self.stdout.write(f'  Created user  {_DEV_EMAIL}')
        else:
            self.stdout.write(f'  User exists   {_DEV_EMAIL}')
        return user

    def _seed_project(self, user, blueprint):
        name, git_url, w_start, w_end, citations, floats, math_count, days_back = blueprint

        project, created = Project.objects.get_or_create(
            owner=user,
            git_url=git_url,
            defaults={
                'name':            name,
                'status':          Project.Status.OK,
                'word_count':      w_end,
                'page_count':      math.ceil(w_end / 300),
                'citation_count':  citations,
                'float_count':     floats,
                'math_count':      math_count,
                'last_synced_at':  timezone.now(),
            },
        )

        verb = 'Created' if created else 'Exists '
        self.stdout.write(f'  {verb} project  "{name}"')

        # Always (re-)generate snapshots so --flush + recreate gives fresh data.
        project.snapshots.all().delete()
        self._generate_snapshots(project, w_start, w_end, citations, floats, math_count, days_back)
        self.stdout.write(f'            → {days_back} snapshots written')

        return project

    def _generate_snapshots(self, project, w_start, w_end, citations, floats, math_count, days_back):
        rng = random.Random(project.git_url)   # deterministic per project

        now    = timezone.now()
        # Build all snapshot objects first, bulk-insert, then back-date taken_at.
        snapshots = []
        for i in range(days_back):
            # day 0 = (days_back - 1) days ago, day (days_back-1) = today
            days_ago = days_back - 1 - i
            t = now - timezone.timedelta(days=days_ago)

            progress = i / max(days_back - 1, 1)  # 0.0 → 1.0
            # Ease-in curve: slow start, faster towards the end
            eased    = progress ** 1.4
            base     = w_start + (w_end - w_start) * eased
            noise    = rng.randint(-200, 200)
            words    = max(0, round(base + noise))
            pages    = math.ceil(words / 300)

            # Citations / floats / math grow proportionally with some lag
            cit   = round(citations  * min(1.0, eased * 1.1))
            flt   = round(floats     * min(1.0, eased * 1.1))
            mth   = round(math_count * min(1.0, eased * 1.1))

            snapshots.append(ProjectSnapshot(
                project        = project,
                word_count     = words,
                page_count     = pages,
                citation_count = cit,
                float_count    = flt,
                math_count     = mth,
            ))

        created = ProjectSnapshot.objects.bulk_create(snapshots)

        # Back-date taken_at — auto_now_add prevents setting it in create(),
        # so we update each row individually using its pk.
        for obj, i in zip(created, range(days_back)):
            days_ago = days_back - 1 - i
            t = now - timezone.timedelta(days=days_ago)
            ProjectSnapshot.objects.filter(pk=obj.pk).update(taken_at=t)

    def _seed_group(self, user, projects):
        group, created = ProjectGroup.objects.get_or_create(
            created_by=user,
            name=_GROUP_NAME,
        )
        verb = 'Created' if created else 'Exists '
        self.stdout.write(f'  {verb} group   "{_GROUP_NAME}"')

        GroupMembership.objects.get_or_create(
            group=group, user=user,
            defaults={'role': GroupMembership.Role.ADMIN},
        )
        for project in projects:
            GroupProject.objects.get_or_create(
                group=group, project=project,
                defaults={'added_by': user},
            )
