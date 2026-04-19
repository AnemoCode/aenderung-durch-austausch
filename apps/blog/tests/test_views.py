import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Comment, Like, Topic, TopicPart

User = get_user_model()


class TopicDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='d@example.com', name='Detail User', password='pw')
        cls.topic = Topic.objects.create(
            title='Testthema', author=cls.user, is_published=True
        )
        cls.part = TopicPart.objects.create(
            topic=cls.topic, author=cls.user, heading='Einleitung', body='Inhalt', order=0
        )
        cls.url = reverse('blog:topic_detail', kwargs={'slug': cls.topic.slug})
        cls.unpublished = Topic.objects.create(
            title='Hidden', author=cls.user, is_published=False, slug='hidden-topic'
        )

    def test_published_topic_returns_200(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_unpublished_topic_returns_404(self):
        url = reverse('blog:topic_detail', kwargs={'slug': self.unpublished.slug})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_context_contains_parts_and_comment_form(self):
        res = self.client.get(self.url)
        self.assertIn('parts', res.context)
        self.assertIn('comment_form', res.context)

    def test_user_liked_false_for_anonymous(self):
        res = self.client.get(self.url)
        self.assertFalse(res.context['user_liked'])

    def test_user_liked_true_when_liked(self):
        Like.objects.create(topic=self.topic, user=self.user)
        self.client.force_login(self.user)
        res = self.client.get(self.url)
        self.assertTrue(res.context['user_liked'])

    def test_post_comment_authenticated(self):
        self.client.force_login(self.user)
        res = self.client.post(self.url, {'body': 'Toller Artikel!'})
        self.assertRedirects(res, self.topic.get_absolute_url())
        self.assertTrue(Comment.objects.filter(topic=self.topic, body='Toller Artikel!').exists())

    def test_post_comment_anonymous_redirects_to_login(self):
        res = self.client.post(self.url, {'body': 'Anonym'})
        self.assertIn('/login/', res.url)
        self.assertEqual(res.status_code, 302)

    def test_post_empty_comment_re_renders_form(self):
        self.client.force_login(self.user)
        res = self.client.post(self.url, {'body': ''})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Comment.objects.filter(topic=self.topic, body='').exists())


class TopicLikeToggleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='like@example.com', name='Liker', password='pw')
        cls.topic = Topic.objects.create(
            title='Likeable', author=cls.user, is_published=True
        )
        cls.url = reverse('blog:topic_like_toggle', kwargs={'slug': cls.topic.slug})

    def test_get_returns_405(self):
        self.client.force_login(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 405)

    def test_anonymous_returns_401(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.content)
        self.assertIn('error', data)

    def test_like_creates_like(self):
        self.client.force_login(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertTrue(data['liked'])
        self.assertEqual(data['count'], 1)
        self.assertTrue(Like.objects.filter(topic=self.topic, user=self.user).exists())

    def test_unlike_removes_like(self):
        Like.objects.create(topic=self.topic, user=self.user)
        self.client.force_login(self.user)
        res = self.client.post(self.url)
        data = json.loads(res.content)
        self.assertFalse(data['liked'])
        self.assertEqual(data['count'], 0)
        self.assertFalse(Like.objects.filter(topic=self.topic, user=self.user).exists())

    def test_unpublished_topic_returns_404(self):
        unpub = Topic.objects.create(
            title='Unpub', author=self.user, is_published=False, slug='unpub-like'
        )
        url = reverse('blog:topic_like_toggle', kwargs={'slug': unpub.slug})
        self.client.force_login(self.user)
        res = self.client.post(url)
        self.assertEqual(res.status_code, 404)


class PostDetailRedirectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='r@example.com', name='Redirect', password='pw')
        cls.topic = Topic.objects.create(
            title='Legacy Topic', author=cls.user, is_published=True, legacy_post_id=42
        )

    def test_redirects_to_topic_url(self):
        url = reverse('blog:post_detail', kwargs={'pk': 42})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 301)
        self.assertIn(self.topic.slug, res.url)

    def test_missing_legacy_id_returns_404(self):
        url = reverse('blog:post_detail', kwargs={'pk': 9999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)


class TagDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='t@example.com', name='Tag User', password='pw')
        cls.topic = Topic.objects.create(
            title='Tagged Topic', author=cls.user, is_published=True
        )
        cls.topic.tags.add('klima')
        cls.part = TopicPart.objects.create(
            topic=cls.topic, author=cls.user, heading='Tagged Part', body='x', order=0
        )
        cls.part.tags.add('klima')

    def test_tag_page_returns_200(self):
        res = self.client.get(reverse('tag_detail', kwargs={'slug': 'klima'}))
        self.assertEqual(res.status_code, 200)

    def test_tag_page_contains_tagged_topic(self):
        res = self.client.get(reverse('tag_detail', kwargs={'slug': 'klima'}))
        self.assertIn(self.topic, res.context['topics'])

    def test_tag_page_contains_tagged_part(self):
        res = self.client.get(reverse('tag_detail', kwargs={'slug': 'klima'}))
        self.assertIn(self.part, res.context['parts'])

    def test_unknown_tag_returns_404(self):
        res = self.client.get(reverse('tag_detail', kwargs={'slug': 'nonexistent-tag'}))
        self.assertEqual(res.status_code, 404)


class HealthCheckTests(TestCase):
    def test_health_returns_ok(self):
        res = self.client.get(reverse('health'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, b'ok')


class LandingPageTests(TestCase):
    def test_landing_page_returns_200(self):
        res = self.client.get(reverse('landing'))
        self.assertEqual(res.status_code, 200)
