from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from apps.blog.models import Comment, Like, Topic, TopicPart

User = get_user_model()


class TopicModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='u@example.com', name='User', password='pw')

    def _make_topic(self, title='Test Thema', **kwargs):
        return Topic.objects.create(title=title, author=self.user, **kwargs)

    def test_str_returns_title(self):
        topic = self._make_topic()
        self.assertEqual(str(topic), 'Test Thema')

    def test_get_absolute_url(self):
        topic = self._make_topic()
        self.assertIn(topic.slug, topic.get_absolute_url())

    def test_slug_auto_generated_from_title(self):
        topic = self._make_topic(title='Klimawandel Basics')
        self.assertEqual(topic.slug, 'klimawandel-basics')

    def test_slug_not_overwritten_if_provided(self):
        topic = self._make_topic(title='Anything', slug='my-custom-slug')
        self.assertEqual(topic.slug, 'my-custom-slug')

    def test_slug_collision_gets_counter(self):
        t1 = self._make_topic(title='Klimawandel')
        t2 = self._make_topic(title='Klimawandel')
        self.assertEqual(t1.slug, 'klimawandel')
        self.assertEqual(t2.slug, 'klimawandel-1')

    def test_multiple_slug_collisions_increment_counter(self):
        t1 = self._make_topic(title='Energie')
        t2 = self._make_topic(title='Energie')
        t3 = self._make_topic(title='Energie')
        self.assertEqual(t1.slug, 'energie')
        self.assertEqual(t2.slug, 'energie-1')
        self.assertEqual(t3.slug, 'energie-2')

    def test_slug_fallback_for_non_ascii_title(self):
        topic = self._make_topic(title='!!!')
        self.assertTrue(topic.slug.startswith('thema'))

    def test_default_is_published_false(self):
        topic = self._make_topic()
        self.assertFalse(topic.is_published)

    def test_is_published_can_be_set(self):
        topic = self._make_topic(is_published=True)
        self.assertTrue(topic.is_published)

    def test_legacy_post_id_nullable(self):
        topic = self._make_topic()
        self.assertIsNone(topic.legacy_post_id)

    def test_legacy_post_id_unique(self):
        self._make_topic(title='T1', legacy_post_id=1)
        with self.assertRaises(IntegrityError):
            self._make_topic(title='T2', legacy_post_id=1)

    def test_ordering_newest_first(self):
        t1 = self._make_topic(title='First')
        t2 = self._make_topic(title='Second')
        topics = list(Topic.objects.all())
        self.assertEqual(topics[0], t2)
        self.assertEqual(topics[1], t1)


class TopicPartModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='p@example.com', name='Author', password='pw')
        cls.topic = Topic.objects.create(title='My Topic', author=cls.user, is_published=True)

    def test_str_format(self):
        part = TopicPart.objects.create(
            topic=self.topic, author=self.user, heading='Teil 1', body='Inhalt', order=0
        )
        self.assertEqual(str(part), 'My Topic — Teil 1')

    def test_ordering_by_order_then_created_at(self):
        p2 = TopicPart.objects.create(
            topic=self.topic, author=self.user, heading='B', body='x', order=1
        )
        p1 = TopicPart.objects.create(
            topic=self.topic, author=self.user, heading='A', body='x', order=0
        )
        parts = list(TopicPart.objects.filter(topic=self.topic))
        self.assertEqual(parts[0], p1)
        self.assertEqual(parts[1], p2)


class CommentModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='c@example.com', name='Commenter', password='pw')
        cls.topic = Topic.objects.create(title='Commented Topic', author=cls.user, is_published=True)

    def test_str_format(self):
        comment = Comment.objects.create(
            topic=self.topic, author=self.user, body='Guter Artikel!'
        )
        self.assertEqual(str(comment), 'Commenter → Commented Topic')

    def test_ordering_oldest_first(self):
        c1 = Comment.objects.create(topic=self.topic, author=self.user, body='First')
        c2 = Comment.objects.create(topic=self.topic, author=self.user, body='Second')
        comments = list(Comment.objects.filter(topic=self.topic))
        self.assertEqual(comments[0], c1)
        self.assertEqual(comments[1], c2)


class LikeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='l@example.com', name='Liker', password='pw')
        cls.topic = Topic.objects.create(title='Liked Topic', author=cls.user, is_published=True)

    def test_str_format(self):
        like = Like.objects.create(topic=self.topic, user=self.user)
        self.assertEqual(str(like), 'Liker → Liked Topic')

    def test_unique_together_prevents_duplicate_likes(self):
        Like.objects.create(topic=self.topic, user=self.user)
        with self.assertRaises(IntegrityError):
            Like.objects.create(topic=self.topic, user=self.user)
