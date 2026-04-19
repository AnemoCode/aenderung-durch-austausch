from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.blog.forms import CommentForm, TopicPartCreateForm
from apps.blog.models import Topic

User = get_user_model()


class CommentFormTests(TestCase):
    def test_valid_form(self):
        form = CommentForm(data={'body': 'Sehr interessant!'})
        self.assertTrue(form.is_valid())

    def test_empty_body_is_invalid(self):
        form = CommentForm(data={'body': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)


class TopicPartCreateFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='f@example.com', name='Form User', password='pw')
        cls.topic = Topic.objects.create(title='Existing Topic', author=cls.user, is_published=True)

    def _base_data(self, **overrides):
        data = {
            'topic': '',
            'new_topic_title': 'Fresh Topic',
            'heading': 'Part Heading',
            'body': 'Part body text',
            'tags': '',
        }
        data.update(overrides)
        return data

    def test_valid_with_new_topic_title(self):
        form = TopicPartCreateForm(data=self._base_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_with_existing_topic(self):
        form = TopicPartCreateForm(data=self._base_data(
            topic=self.topic.pk, new_topic_title=''
        ))
        self.assertTrue(form.is_valid(), form.errors)

    def test_both_topic_and_new_title_invalid(self):
        form = TopicPartCreateForm(data=self._base_data(
            topic=self.topic.pk, new_topic_title='Another'
        ))
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())

    def test_neither_topic_nor_new_title_invalid(self):
        form = TopicPartCreateForm(data=self._base_data(
            topic='', new_topic_title=''
        ))
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())

    def test_duplicate_title_case_insensitive_invalid(self):
        form = TopicPartCreateForm(data=self._base_data(
            new_topic_title='existing topic'
        ))
        self.assertFalse(form.is_valid())
        self.assertIn('new_topic_title', form.errors)

    def test_missing_heading_invalid(self):
        form = TopicPartCreateForm(data=self._base_data(heading=''))
        self.assertFalse(form.is_valid())
        self.assertIn('heading', form.errors)

    def test_missing_body_invalid(self):
        form = TopicPartCreateForm(data=self._base_data(body=''))
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_parsed_tags_splits_correctly(self):
        form = TopicPartCreateForm(data=self._base_data(tags='klima, energie, wasser'))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.parsed_tags(), ['klima', 'energie', 'wasser'])

    def test_parsed_tags_empty(self):
        form = TopicPartCreateForm(data=self._base_data(tags=''))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.parsed_tags(), [])

    def test_parsed_tags_strips_whitespace(self):
        form = TopicPartCreateForm(data=self._base_data(tags='  klima  ,  energie  '))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.parsed_tags(), ['klima', 'energie'])

    def test_new_topic_title_whitespace_treated_as_empty(self):
        form = TopicPartCreateForm(data=self._base_data(
            topic='', new_topic_title='   '
        ))
        self.assertFalse(form.is_valid())
