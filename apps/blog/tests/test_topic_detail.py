from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Comment, Like, Topic, TopicPart

User = get_user_model()


class TopicDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(email='a@x.de', name='Alice', password='pw')
        cls.user = User.objects.create_user(email='b@x.de', name='Bob', password='pw')
        cls.topic = Topic.objects.create(title='Test Topic', author=cls.author, is_published=True)
        TopicPart.objects.create(
            topic=cls.topic, author=cls.author, heading='Part One', body='Content', order=0,
        )
        cls.url = reverse('blog:topic_detail', kwargs={'slug': cls.topic.slug})

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_unpublished_topic_returns_404(self):
        hidden = Topic.objects.create(title='Hidden', author=self.author, is_published=False)
        url = reverse('blog:topic_detail', kwargs={'slug': hidden.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_liked_false_for_anonymous(self):
        response = self.client.get(self.url)
        self.assertFalse(response.context['user_liked'])

    def test_user_liked_true_when_user_has_liked(self):
        Like.objects.create(topic=self.topic, user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTrue(response.context['user_liked'])

    def test_user_liked_false_when_user_has_not_liked(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertFalse(response.context['user_liked'])

    def test_anonymous_post_comment_redirects_to_login(self):
        response = self.client.post(self.url, {'body': 'A comment'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_post_valid_comment_saves(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'body': 'Great post!'})
        self.assertRedirects(response, self.url)
        self.assertTrue(Comment.objects.filter(body='Great post!', author=self.user).exists())

    def test_post_invalid_comment_rerenders_form(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'body': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(topic=self.topic, author=self.user).exists())

    def test_context_contains_parts(self):
        response = self.client.get(self.url)
        self.assertIn('parts', response.context)
        self.assertEqual(len(response.context['parts']), 1)

    def test_context_contains_comment_form(self):
        response = self.client.get(self.url)
        self.assertIn('comment_form', response.context)
