from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.definitions.models import Definition

User = get_user_model()


class DefinitionModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            email='author@example.com', name='Author', password='pw',
        )

    def _make(self, term='Holocaust', **kwargs):
        defaults = dict(
            term=term,
            simple_explanation='Einfacher Text.',
            formal_explanation='Formaler Text.',
            author=self.author,
        )
        defaults.update(kwargs)
        return Definition.objects.create(**defaults)

    def test_str_returns_term(self):
        d = self._make(term='Rechtsextremismus')
        self.assertEqual(str(d), 'Rechtsextremismus')

    def test_slug_is_auto_generated(self):
        d = self._make(term='Gruppenbezogene Menschenfeindlichkeit')
        self.assertEqual(d.slug, 'gruppenbezogene-menschenfeindlichkeit')

    def test_slug_is_deduplicated(self):
        d1 = self._make(term='Ideologie')
        d2 = self._make(term='ideologie ', simple_explanation='x', formal_explanation='y')
        # clean_term uniqueness is form-level; model allows create via ORM directly.
        self.assertNotEqual(d1.slug, d2.slug)
        self.assertTrue(d2.slug.startswith('ideologie'))

    def test_get_absolute_url(self):
        d = self._make(term='Antisemitismus')
        self.assertEqual(
            d.get_absolute_url(),
            reverse('definitions:detail', kwargs={'slug': d.slug}),
        )

    def test_initial_letter_alphabetic(self):
        self.assertEqual(self._make(term='Holocaust').initial_letter, 'H')

    def test_initial_letter_umlaut_folds_to_base(self):
        self.assertEqual(self._make(term='Ängste').initial_letter, 'A')
        self.assertEqual(self._make(term='Österreich').initial_letter, 'O')
        self.assertEqual(self._make(term='Überfremdung').initial_letter, 'U')

    def test_initial_letter_non_alpha_falls_back_to_hash(self):
        self.assertEqual(self._make(term='1933').initial_letter, '#')
        self.assertEqual(self._make(term='#hashtag').initial_letter, '#')

    def test_ordering_is_alphabetical(self):
        self._make(term='Zionismus')
        self._make(term='Antisemitismus')
        self._make(term='Mobilität')
        terms = list(Definition.objects.values_list('term', flat=True))
        self.assertEqual(terms, ['Antisemitismus', 'Mobilität', 'Zionismus'])

    def test_term_case_insensitive_unique_at_db_level(self):
        self._make(term='Holocaust')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Definition.objects.create(
                    term='holocaust',
                    simple_explanation='x',
                    formal_explanation='y',
                    author=self.author,
                )
