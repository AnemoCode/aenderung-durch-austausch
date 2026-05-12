from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.blog.models import Comment, Like, Topic, TopicPart

User = get_user_model()


class TopicModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(email='a@x.de', name='Author', password='pw')

    def test_str_returns_title(self):
        topic = Topic.objects.create(title='Klimawandel', author=self.author)
        self.assertEqual(str(topic), 'Klimawandel')

    def test_slug_auto_generated(self):
        topic = Topic.objects.create(title='Digitale Bildung', author=self.author)
        self.assertEqual(topic.slug, 'digitale-bildung')

    def test_slug_deduplicated_when_conflict(self):
        t1 = Topic.objects.create(title='Mobilität', author=self.author)
        t2 = Topic.objects.create(title='Mobilität', author=self.author)
        self.assertNotEqual(t1.slug, t2.slug)
        self.assertEqual(t1.slug, 'mobilitat')
        self.assertTrue(t2.slug.startswith('mobilitat-'))

    def test_slug_dedup_increments_counter(self):
        t1 = Topic.objects.create(title='Test Slug', author=self.author)
        t2 = Topic.objects.create(title='Test Slug', author=self.author)
        t3 = Topic.objects.create(title='Test Slug', author=self.author)
        slugs = {t1.slug, t2.slug, t3.slug}
        self.assertEqual(len(slugs), 3)

    def test_slug_falls_back_to_thema_for_non_ascii(self):
        topic = Topic.objects.create(title='αβγ', author=self.author)
        self.assertTrue(topic.slug.startswith('thema'))

    def test_get_absolute_url(self):
        topic = Topic.objects.create(title='Arbeit', author=self.author)
        self.assertIn(topic.slug, topic.get_absolute_url())

    def test_ordering_newest_first(self):
        t1 = Topic.objects.create(title='First', author=self.author)
        t2 = Topic.objects.create(title='Second', author=self.author)
        topics = list(Topic.objects.all())
        self.assertEqual(topics[0], t2)
        self.assertEqual(topics[1], t1)


class TopicPartModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(email='b@x.de', name='Bob', password='pw')
        cls.topic = Topic.objects.create(title='My Topic', author=cls.author)

    def test_str_contains_topic_and_heading(self):
        part = TopicPart.objects.create(
            topic=self.topic, author=self.author, heading='Intro', body='Text', order=0,
        )
        result = str(part)
        self.assertIn('My Topic', result)
        self.assertIn('Intro', result)


class CommentModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(email='c@x.de', name='Carol', password='pw')
        cls.topic = Topic.objects.create(title='Comment Topic', author=cls.author)

    def test_str_contains_author_and_topic(self):
        comment = Comment.objects.create(topic=self.topic, author=self.author, body='Hi')
        result = str(comment)
        self.assertIn('Carol', result)
        self.assertIn('Comment Topic', result)


class LikeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='d@x.de', name='Dave', password='pw')
        cls.topic = Topic.objects.create(title='Like Topic', author=cls.user)

    def test_str_contains_user_and_topic(self):
        like = Like.objects.create(topic=self.topic, user=self.user)
        result = str(like)
        self.assertIn('Dave', result)
        self.assertIn('Like Topic', result)
