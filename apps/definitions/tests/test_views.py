from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.definitions.models import Definition

User = get_user_model()


class DefinitionViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            email='staff@example.com', name='Staff', password='pw',
        )
        cls.staff.is_staff = True
        cls.staff.save()
        cls.other = User.objects.create_user(
            email='other@example.com', name='Other', password='pw',
        )
        cls.holo = Definition.objects.create(
            term='Holocaust',
            simple_explanation='Einfacher Text zum Holocaust.',
            formal_explanation='Formale Definition des Holocaust.',
            author=cls.staff,
        )
        cls.ideo = Definition.objects.create(
            term='Ideologie',
            simple_explanation='Ideen, die Menschen teilen.',
            formal_explanation='System zusammenhängender Ideen.',
            author=cls.staff,
        )
        cls.unpub = Definition.objects.create(
            term='Versteckt',
            simple_explanation='…', formal_explanation='…',
            author=cls.staff, is_published=False,
        )

    # ---- list view -----------------------------------------------------

    def test_list_renders_published_only(self):
        res = self.client.get(reverse('definitions:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Holocaust')
        self.assertContains(res, 'Ideologie')
        self.assertNotContains(res, 'Versteckt')

    def test_list_letter_filter(self):
        res = self.client.get(reverse('definitions:index'), {'letter': 'H'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Holocaust')
        self.assertNotContains(res, 'Ideologie')

    def test_list_query_filter(self):
        res = self.client.get(reverse('definitions:index'), {'q': 'ideen'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Ideologie')
        self.assertNotContains(res, 'Holocaust')

    def test_list_invalid_letter_ignored(self):
        res = self.client.get(reverse('definitions:index'), {'letter': 'ZZZ'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Holocaust')

    def test_list_hash_bucket_filters_non_alpha_terms(self):
        Definition.objects.create(
            term='1933',
            simple_explanation='Machtergreifung.',
            formal_explanation='Jahr der Machtergreifung.',
            author=self.staff,
        )
        # '#' must be URL-encoded as %23; Django decodes it on the server.
        res = self.client.get(reverse('definitions:index'), {'letter': '#'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '1933')
        self.assertNotContains(res, 'Holocaust')
        self.assertNotContains(res, 'Ideologie')

    def test_list_filtered_empty_shows_no_results_not_absolute_empty(self):
        # Search that matches nothing while definitions exist must hit the
        # "Keine Definitionen gefunden" branch, not "Noch keine Definitionen".
        res = self.client.get(
            reverse('definitions:index'), {'q': 'xyzzy-not-a-term'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Keine Definitionen gefunden')
        self.assertNotContains(res, 'Noch keine Definitionen')

    def test_list_absolute_empty_when_no_definitions_exist(self):
        Definition.objects.all().delete()
        res = self.client.get(reverse('definitions:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Noch keine Definitionen')

    # ---- detail view ---------------------------------------------------

    def test_detail_renders_published(self):
        res = self.client.get(self.holo.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Holocaust')
        self.assertContains(res, 'Einfacher Text zum Holocaust.')
        self.assertContains(res, 'Formale Definition des Holocaust.')

    def test_detail_unpublished_404(self):
        res = self.client.get(
            reverse('definitions:detail', kwargs={'slug': self.unpub.slug})
        )
        self.assertEqual(res.status_code, 404)

    # ---- create view ---------------------------------------------------

    def test_create_anonymous_redirects_to_login(self):
        res = self.client.get(reverse('definitions:create'))
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login/', res.url)

    def test_create_non_staff_redirects_to_index(self):
        self.client.force_login(self.other)
        res = self.client.get(reverse('definitions:create'))
        self.assertRedirects(res, reverse('definitions:index'))

    def test_create_staff_sees_form(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('definitions:create'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Neue Definition')

    def test_create_post_creates_definition_with_tags(self):
        self.client.force_login(self.staff)
        res = self.client.post(reverse('definitions:create'), {
            'term': 'Rechtsextremismus',
            'simple_explanation': 'Einfache Erklärung.',
            'formal_explanation': 'Formale Erklärung.',
            'tags': 'politik, rechts',
        })
        d = Definition.objects.get(term='Rechtsextremismus')
        self.assertRedirects(res, d.get_absolute_url())
        self.assertEqual(d.author, self.staff)
        self.assertCountEqual(
            list(d.tags.values_list('name', flat=True)), ['politik', 'rechts'],
        )

    def test_create_rejects_duplicate_term(self):
        self.client.force_login(self.staff)
        res = self.client.post(reverse('definitions:create'), {
            'term': 'holocaust',
            'simple_explanation': 'x',
            'formal_explanation': 'y',
            'tags': '',
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Definition.objects.filter(term__iexact='holocaust').count(), 1)

    # ---- update view ---------------------------------------------------

    def test_update_non_staff_redirects(self):
        self.client.force_login(self.other)
        res = self.client.get(
            reverse('definitions:edit', kwargs={'slug': self.holo.slug})
        )
        self.assertRedirects(res, reverse('definitions:index'))

    def test_update_staff_can_edit_and_replace_tags(self):
        self.holo.tags.add('alt')
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse('definitions:edit', kwargs={'slug': self.holo.slug}),
            {
                'term': 'Holocaust',
                'simple_explanation': 'Neu einfach.',
                'formal_explanation': 'Neu formal.',
                'tags': 'neu',
            },
        )
        self.holo.refresh_from_db()
        self.assertRedirects(res, self.holo.get_absolute_url())
        self.assertEqual(self.holo.simple_explanation, 'Neu einfach.')
        self.assertCountEqual(
            list(self.holo.tags.values_list('name', flat=True)), ['neu'],
        )
