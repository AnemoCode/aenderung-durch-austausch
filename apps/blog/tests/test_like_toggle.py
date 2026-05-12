import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Like, Topic

User = get_user_model()


class TopicLikeToggleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='a@x.de', name='Alice', password='pw')
        cls.topic = Topic.objects.create(
            title='Likeable Topic', author=cls.user, is_published=True,
        )
        cls.url = reverse('blog:topic_like_toggle', kwargs={'slug': cls.topic.slug})

    def test_get_returns_405(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_anonymous_returns_401(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_like_creates_like(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['liked'])
        self.assertEqual(data['count'], 1)
        self.assertTrue(Like.objects.filter(topic=self.topic, user=self.user).exists())

    def test_unlike_removes_like(self):
        Like.objects.create(topic=self.topic, user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['liked'])
        self.assertFalse(Like.objects.filter(topic=self.topic, user=self.user).exists())

    def test_nonexistent_topic_returns_404(self):
        self.client.force_login(self.user)
        url = reverse('blog:topic_like_toggle', kwargs={'slug': 'does-not-exist'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_unpublished_topic_returns_404(self):
        unpublished = Topic.objects.create(
            title='Draft', author=self.user, is_published=False,
        )
        self.client.force_login(self.user)
        url = reverse('blog:topic_like_toggle', kwargs={'slug': unpublished.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
