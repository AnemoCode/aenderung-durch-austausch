from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.definitions.forms import DefinitionForm
from apps.definitions.models import Definition

User = get_user_model()


class DefinitionFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            email='a@example.com', name='A', password='pw',
        )

    def test_valid_form_saves_and_parses_tags(self):
        form = DefinitionForm(data={
            'term': 'Holocaust',
            'simple_explanation': 'Einfache Erklärung.',
            'formal_explanation': 'Formale Erklärung.',
            'tags': 'geschichte, antisemitismus',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.parsed_tags(), ['geschichte', 'antisemitismus'])

    def test_both_explanations_required(self):
        form = DefinitionForm(data={
            'term': 'Begriff',
            'simple_explanation': '',
            'formal_explanation': '',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('simple_explanation', form.errors)
        self.assertIn('formal_explanation', form.errors)

    def test_duplicate_term_rejected_case_insensitive(self):
        Definition.objects.create(
            term='Holocaust',
            simple_explanation='…', formal_explanation='…',
            author=self.author,
        )
        form = DefinitionForm(data={
            'term': 'holocaust',
            'simple_explanation': 'x',
            'formal_explanation': 'y',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)

    def test_editing_same_instance_allows_same_term(self):
        d = Definition.objects.create(
            term='Holocaust',
            simple_explanation='a', formal_explanation='b',
            author=self.author,
        )
        form = DefinitionForm(
            data={
                'term': 'Holocaust',
                'simple_explanation': 'neu',
                'formal_explanation': 'neu2',
                'tags': '',
            },
            instance=d,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_tags_parse_to_empty_list(self):
        form = DefinitionForm(data={
            'term': 'X',
            'simple_explanation': 'a',
            'formal_explanation': 'b',
            'tags': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.parsed_tags(), [])

    def test_empty_simple_explanation_rejected(self):
        form = DefinitionForm(data={
            'term': 'Begriff',
            'simple_explanation': '',
            'formal_explanation': 'Formale Erklärung.',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('simple_explanation', form.errors)

    def test_empty_formal_explanation_rejected(self):
        form = DefinitionForm(data={
            'term': 'Begriff2',
            'simple_explanation': 'Einfache Erklärung.',
            'formal_explanation': '',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('formal_explanation', form.errors)

    def test_whitespace_only_explanation_rejected(self):
        form = DefinitionForm(data={
            'term': 'Begriff3',
            'simple_explanation': '   ',
            'formal_explanation': 'Formale Erklärung.',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('simple_explanation', form.errors)

    def test_html_only_simple_explanation_rejected(self):
        # Empty tags that sanitize to no visible text hit the clean_simple_explanation raise path
        form = DefinitionForm(data={
            'term': 'Begriff4',
            'simple_explanation': '<p></p>',
            'formal_explanation': 'Formale Erklärung.',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('simple_explanation', form.errors)

    def test_html_only_formal_explanation_rejected(self):
        # Empty tags that sanitize to no visible text hit the clean_formal_explanation raise path
        form = DefinitionForm(data={
            'term': 'Begriff5',
            'simple_explanation': 'Einfache Erklärung.',
            'formal_explanation': '<p></p>',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('formal_explanation', form.errors)
