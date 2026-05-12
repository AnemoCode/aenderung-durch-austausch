from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Topic

User = get_user_model()


class PostDetailRedirectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(email='a@x.de', name='Author', password='pw')
        cls.topic = Topic.objects.create(
            title='Legacy Post Topic',
            author=cls.author,
            is_published=True,
            legacy_post_id=42,
        )

    def test_redirect_to_topic_detail(self):
        url = reverse('blog:post_detail', kwargs={'pk': 42})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, self.topic.get_absolute_url(), status_code=301)

    def test_nonexistent_legacy_id_returns_404(self):
        url = reverse('blog:post_detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_unpublished_topic_returns_404(self):
        Topic.objects.create(
            title='Unpublished Legacy',
            author=self.author,
            is_published=False,
            legacy_post_id=99,
        )
        url = reverse('blog:post_detail', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
