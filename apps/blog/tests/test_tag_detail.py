from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Topic, TopicPart
from apps.definitions.models import Definition

User = get_user_model()


class TagDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(email='a@x.de', name='Author', password='pw')
        cls.topic = Topic.objects.create(
            title='Climate Topic', author=cls.author, is_published=True,
        )
        cls.topic.tags.add('climate')
        cls.part = TopicPart.objects.create(
            topic=cls.topic, author=cls.author, heading='Climate Part', body='Text', order=0,
        )
        cls.part.tags.add('climate')
        cls.definition = Definition.objects.create(
            term='Climate Change',
            simple_explanation='Simple.',
            formal_explanation='Formal.',
            author=cls.author,
            is_published=True,
        )
        cls.definition.tags.add('climate')

    def _url(self, slug):
        return reverse('tag_detail', kwargs={'slug': slug})

    def test_existing_tag_returns_200(self):
        response = self.client.get(self._url('climate'))
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_tag_returns_404(self):
        response = self.client.get(self._url('nonexistent-tag-xyz'))
        self.assertEqual(response.status_code, 404)

    def test_context_contains_tagged_topics(self):
        response = self.client.get(self._url('climate'))
        self.assertIn(self.topic, response.context['topics'])

    def test_context_contains_tagged_parts(self):
        response = self.client.get(self._url('climate'))
        self.assertIn(self.part, response.context['parts'])

    def test_context_contains_tagged_definitions(self):
        response = self.client.get(self._url('climate'))
        self.assertIn(self.definition, response.context['definitions'])

    def test_unpublished_topic_excluded(self):
        hidden = Topic.objects.create(
            title='Hidden Climate', author=self.author, is_published=False,
        )
        hidden.tags.add('climate')
        response = self.client.get(self._url('climate'))
        self.assertNotIn(hidden, response.context['topics'])

    def test_context_tag_matches(self):
        response = self.client.get(self._url('climate'))
        self.assertEqual(response.context['tag'].slug, 'climate')
