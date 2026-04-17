from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Like, Topic, TopicPart

User = get_user_model()


class IndexGroupingSortingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('blog:index')
        cls.alice = User.objects.create_user(email='a@x.de', name='Alice A', password='pw')
        cls.bob = User.objects.create_user(email='b@x.de', name='Bob B', password='pw')

        cls.topic_a = Topic.objects.create(title='Topic A', author=cls.alice, is_published=True)
        cls.topic_b = Topic.objects.create(title='Topic B', author=cls.alice, is_published=True)
        cls.hidden = Topic.objects.create(title='Hidden', author=cls.alice, is_published=False)

        cls.part_a1 = TopicPart.objects.create(
            topic=cls.topic_a, author=cls.alice, heading='A1', body='…', order=0,
        )
        cls.part_a2 = TopicPart.objects.create(
            topic=cls.topic_a, author=cls.bob, heading='A2', body='…', order=1,
        )
        cls.part_b1 = TopicPart.objects.create(
            topic=cls.topic_b, author=cls.bob, heading='B1', body='…', order=0,
        )
        TopicPart.objects.create(
            topic=cls.hidden, author=cls.alice, heading='H1', body='…', order=0,
        )
        # Give topic_b one like
        Like.objects.create(topic=cls.topic_b, user=cls.alice)

    def test_unpublished_topics_hidden(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, 'H1')
        self.assertEqual(res.context['total_parts'], 3)

    def test_default_group_is_topic(self):
        res = self.client.get(self.url)
        self.assertEqual(res.context['group'], 'topic')
        groups = res.context['groups']
        keys = [g[0] for g in groups]
        self.assertIn(self.topic_a.pk, keys)
        self.assertIn(self.topic_b.pk, keys)

    def test_group_by_author(self):
        res = self.client.get(self.url, {'group': 'author'})
        self.assertEqual(res.context['group'], 'author')
        author_keys = {g[0] for g in res.context['groups']}
        self.assertEqual(author_keys, {self.alice.pk, self.bob.pk})

    def test_group_none(self):
        res = self.client.get(self.url, {'group': 'none'})
        self.assertEqual(res.context['group'], 'none')
        self.assertEqual(len(res.context['groups']), 1)

    def test_sort_likes_desc_puts_topic_b_parts_first(self):
        res = self.client.get(self.url, {'group': 'none', 'sort': 'likes_desc'})
        parts = res.context['groups'][0][3]
        # topic_b has a like → its part must come first
        self.assertEqual(parts[0].topic, self.topic_b)

    def test_sort_date_asc_reverses_order(self):
        res_desc = self.client.get(self.url, {'group': 'none', 'sort': 'date_desc'})
        res_asc = self.client.get(self.url, {'group': 'none', 'sort': 'date_asc'})
        desc_ids = [p.pk for p in res_desc.context['groups'][0][3]]
        asc_ids = [p.pk for p in res_asc.context['groups'][0][3]]
        self.assertEqual(desc_ids, list(reversed(asc_ids)))

    def test_invalid_params_fall_back_to_defaults(self):
        res = self.client.get(self.url, {'group': 'bogus', 'sort': 'bogus'})
        self.assertEqual(res.context['group'], 'topic')
        self.assertEqual(res.context['sort'], 'date_desc')
