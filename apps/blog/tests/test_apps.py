from unittest.mock import patch

from django.test import TestCase

from apps.blog.apps import _create_moderator_group


class CreateModeratorGroupTests(TestCase):
    def test_creates_moderator_group(self):
        from django.contrib.auth.models import Group
        Group.objects.filter(name='Moderator').delete()
        _create_moderator_group(sender=None)
        self.assertTrue(Group.objects.filter(name='Moderator').exists())

    def test_idempotent_when_group_exists(self):
        from django.contrib.auth.models import Group
        _create_moderator_group(sender=None)
        _create_moderator_group(sender=None)
        self.assertEqual(Group.objects.filter(name='Moderator').count(), 1)

    def test_handles_exception_gracefully(self):
        with patch('django.contrib.auth.models.Group.objects.get_or_create', side_effect=Exception('DB error')):
            try:
                _create_moderator_group(sender=None)
            except Exception:
                self.fail('_create_moderator_group raised an exception')

    def test_warning_printed_when_no_permissions(self):
        from io import StringIO
        from django.contrib.auth.models import Permission
        with patch.object(Permission.objects, 'filter') as mock_filter:
            mock_qs = mock_filter.return_value
            mock_qs.exists.return_value = False
            mock_qs.set = lambda *a, **kw: None
            captured = StringIO()
            with patch('sys.stderr', captured):
                _create_moderator_group(sender=None)
