from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from apps.definitions.models import Definition

User = get_user_model()


def _get_moderator_group():
    group, _ = Group.objects.get_or_create(name='Moderator')
    perms = Permission.objects.filter(content_type__app_label='definitions')
    group.permissions.add(*perms)
    return group


class ModeratorDefinitionCreateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.create_url = reverse('definitions:create')
        cls.moderator = User.objects.create_user(
            email='mod@example.com', name='Mod User', password='pw',
        )
        cls.moderator.groups.add(_get_moderator_group())
        cls.regular = User.objects.create_user(
            email='regular@example.com', name='Regular User', password='pw',
        )

    def test_moderator_can_access_create_form(self):
        self.client.force_login(self.moderator)
        res = self.client.get(self.create_url)
        self.assertEqual(res.status_code, 200)

    def test_regular_user_cannot_access_create_form(self):
        self.client.force_login(self.regular)
        res = self.client.get(self.create_url)
        self.assertRedirects(res, reverse('definitions:index'))

    def test_create_button_visible_to_moderator(self):
        self.client.force_login(self.moderator)
        res = self.client.get(reverse('definitions:index'))
        self.assertContains(res, reverse('definitions:create'))

    def test_create_button_hidden_from_regular_user(self):
        self.client.force_login(self.regular)
        res = self.client.get(reverse('definitions:index'))
        self.assertNotContains(res, reverse('definitions:create'))


class ModeratorDefinitionEditTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moderator = User.objects.create_user(
            email='mod@example.com', name='Mod User', password='pw',
        )
        cls.moderator.groups.add(_get_moderator_group())
        cls.regular = User.objects.create_user(
            email='regular@example.com', name='Regular User', password='pw',
        )
        cls.definition = Definition.objects.create(
            term='Testbegriff',
            simple_explanation='<p>Einfach</p>',
            formal_explanation='<p>Formal</p>',
            author=cls.moderator,
            is_published=True,
        )

    def test_moderator_can_access_edit_form(self):
        self.client.force_login(self.moderator)
        res = self.client.get(reverse('definitions:edit', kwargs={'slug': self.definition.slug}))
        self.assertEqual(res.status_code, 200)

    def test_regular_user_cannot_access_edit_form(self):
        self.client.force_login(self.regular)
        res = self.client.get(reverse('definitions:edit', kwargs={'slug': self.definition.slug}))
        self.assertRedirects(res, reverse('definitions:index'))

    def test_edit_button_visible_to_moderator(self):
        self.client.force_login(self.moderator)
        res = self.client.get(self.definition.get_absolute_url())
        self.assertContains(res, reverse('definitions:edit', kwargs={'slug': self.definition.slug}))

    def test_edit_button_hidden_from_regular_user(self):
        self.client.force_login(self.regular)
        res = self.client.get(self.definition.get_absolute_url())
        self.assertNotContains(res, reverse('definitions:edit', kwargs={'slug': self.definition.slug}))
