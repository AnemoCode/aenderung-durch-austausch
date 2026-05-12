from unittest.mock import patch

from django.test import TestCase

from apps.definitions.apps import _add_definitions_to_moderator_group


class AddDefinitionsToModeratorGroupTests(TestCase):
    def test_adds_definitions_permissions_to_moderator_group(self):
        from django.contrib.auth.models import Group, Permission
        group, _ = Group.objects.get_or_create(name='Moderator')
        _add_definitions_to_moderator_group(sender=None)
        codenames = set(group.permissions.values_list('codename', flat=True))
        self.assertTrue(
            any(c.startswith(('add_', 'change_', 'delete_', 'view_')) for c in codenames)
        )

    def test_handles_exception_gracefully(self):
        with patch('django.contrib.auth.models.Group.objects.get_or_create', side_effect=Exception('DB error')):
            try:
                _add_definitions_to_moderator_group(sender=None)
            except Exception:
                self.fail('_add_definitions_to_moderator_group raised an exception')
