from django.test import TestCase

from apps.medienkompetenz.forms import (
    AiImageQuizForm,
    ArticleForm,
    FramingExerciseForm,
    TextCalloutForm,
)


class ArticleFormSanitizeTest(TestCase):
    def test_strips_script_tags_from_body(self):
        form = ArticleForm(data={
            'title': 'Test',
            'lead': '',
            'body': '<p>hi</p><script>alert(1)</script>',
            'references': '',
            'is_published': True,
            'tags': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn('<script>', form.cleaned_data['body'])
        self.assertIn('<p>hi</p>', form.cleaned_data['body'])

    def test_empty_body_is_rejected(self):
        form = ArticleForm(data={
            'title': 'Test',
            'lead': '',
            'body': '   <p>  </p>',
            'references': '',
            'is_published': True,
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_preserves_image_resize_width_style(self):
        # The Quill image-resize module stores the dragged size as an inline
        # width style; it must survive sanitization so editors can size images.
        form = ArticleForm(data={
            'title': 'Test',
            'lead': '',
            'body': '<p>Bild:</p><p><img src="/media/x.png" style="width: 320px;"></p>',
            'references': '',
            'is_published': True,
            'tags': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn('width: 320px', form.cleaned_data['body'])

    def test_strips_disallowed_style_property_from_image(self):
        form = ArticleForm(data={
            'title': 'Test',
            'lead': '',
            'body': '<p>Bild:</p><p><img src="/media/x.png" style="position: fixed; width: 50px;"></p>',
            'references': '',
            'is_published': True,
            'tags': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        body = form.cleaned_data['body']
        self.assertNotIn('position', body)
        self.assertIn('width: 50px', body)


class AiImageQuizFormTest(TestCase):
    def test_valid_items_produce_structured_data(self):
        form = AiImageQuizForm(data={
            'title': 'Quiz',
            'instructions': '',
            'items_raw': '/media/a.jpg | ki | Sieh die Hände\n/media/b.jpg | echt | Klar real',
        })
        self.assertTrue(form.is_valid(), form.errors)
        items = form.cleaned_data['items_raw']
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['is_ai'], True)
        self.assertEqual(items[1]['is_ai'], False)

    def test_unknown_answer_is_rejected(self):
        form = AiImageQuizForm(data={
            'title': '',
            'instructions': '',
            'items_raw': '/media/a.jpg | maybe',
        })
        self.assertFalse(form.is_valid())

    def test_empty_items_rejected(self):
        form = AiImageQuizForm(data={'items_raw': ''})
        self.assertFalse(form.is_valid())


class FramingExerciseFormTest(TestCase):
    def test_valid_scenario_with_correct_option(self):
        form = FramingExerciseForm(data={
            'title': '',
            'instructions': '',
            'scenarios_raw': 'Flüchtlingswelle\nNeutral\n*Negativ konnotiert\n> Wasser-Metapher entmenschlicht',
        })
        self.assertTrue(form.is_valid(), form.errors)
        scenarios = form.cleaned_data['scenarios_raw']
        self.assertEqual(len(scenarios), 1)
        self.assertEqual(scenarios[0]['prompt'], 'Flüchtlingswelle')
        self.assertEqual(len(scenarios[0]['options']), 2)
        self.assertTrue(scenarios[0]['options'][1]['is_correct'])

    def test_scenario_without_correct_option_rejected(self):
        form = FramingExerciseForm(data={
            'scenarios_raw': 'Prompt\nA\nB',
        })
        self.assertFalse(form.is_valid())

    def test_single_option_rejected(self):
        form = FramingExerciseForm(data={
            'scenarios_raw': 'Prompt\n*A',
        })
        self.assertFalse(form.is_valid())


class TextCalloutFormTest(TestCase):
    def test_builds_expected_data(self):
        form = TextCalloutForm(data={
            'title': 'Achtung',
            'instructions': '',
            'tone': 'warning',
            'body': '<p>Vorsicht</p>',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.build_data()['tone'], 'warning')
        self.assertIn('<p>Vorsicht</p>', form.build_data()['body'])
