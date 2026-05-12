from django.test import TestCase

from apps.blog.forms import CommentForm, TopicPartCreateForm, TopicPartEditForm


class CommentFormTests(TestCase):
    def test_valid_comment_form(self):
        form = CommentForm(data={'body': 'A valid comment'})
        self.assertTrue(form.is_valid())

    def test_empty_body_invalid(self):
        form = CommentForm(data={'body': ''})
        self.assertFalse(form.is_valid())


class TopicPartCreateFormBodyValidationTests(TestCase):
    def test_empty_body_rejected(self):
        form = TopicPartCreateForm(data={
            'topic': '',
            'new_topic_title': 'New Topic',
            'heading': 'Heading',
            'body': '',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_whitespace_only_body_rejected(self):
        form = TopicPartCreateForm(data={
            'topic': '',
            'new_topic_title': 'New Topic 2',
            'heading': 'Heading',
            'body': '   ',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_html_only_body_rejected(self):
        # Empty tags that sanitize to no visible text hit the clean_body raise path
        form = TopicPartCreateForm(data={
            'topic': '',
            'new_topic_title': 'New Topic 3',
            'heading': 'Heading',
            'body': '<p></p>',
            'tags': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_tags_with_whitespace_trimmed(self):
        from apps.blog.models import Topic
        from django.contrib.auth import get_user_model
        User = get_user_model()
        author = User.objects.create_user(email='x@x.de', name='X', password='pw')
        topic = Topic.objects.create(title='Test Form Topic', author=author)
        form = TopicPartCreateForm(data={
            'topic': topic.pk,
            'new_topic_title': '',
            'heading': 'Heading',
            'body': '<p>Content</p>',
            'tags': '  klima , energie  ',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.parsed_tags(), ['klima', 'energie'])


class TopicPartEditFormTests(TestCase):
    def test_valid_edit_form(self):
        form = TopicPartEditForm(data={
            'heading': 'New Heading',
            'body': '<p>Content</p>',
            'tags': 'tag1, tag2',
        })
        self.assertTrue(form.is_valid())

    def test_empty_heading_invalid(self):
        form = TopicPartEditForm(data={
            'heading': '',
            'body': '<p>Content</p>',
            'tags': '',
        })
        self.assertFalse(form.is_valid())

    def test_parsed_tags_empty(self):
        form = TopicPartEditForm(data={
            'heading': 'H',
            'body': '<p>Body</p>',
            'tags': '',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.parsed_tags(), [])
