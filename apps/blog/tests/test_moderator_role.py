from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Comment, Topic, TopicPart

User = get_user_model()


def _get_moderator_group():
    group, _ = Group.objects.get_or_create(name='Moderator')
    perms = Permission.objects.filter(
        codename__in=['add_topicpart', 'add_comment', 'delete_comment'],
        content_type__app_label='blog',
    )
    group.permissions.set(perms)
    return group


class ModeratorPostCreateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('blog:post_create')
        cls.moderator = User.objects.create_user(
            email='mod@example.com', name='Mod User', password='pw',
        )
        cls.moderator.groups.add(_get_moderator_group())
        cls.regular = User.objects.create_user(
            email='regular@example.com', name='Regular User', password='pw',
        )
        cls.existing_topic = Topic.objects.create(
            title='Test Topic', author=cls.moderator, is_published=True,
        )

    def test_moderator_can_access_post_form(self):
        self.client.force_login(self.moderator)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_regular_user_cannot_access_post_form(self):
        self.client.force_login(self.regular)
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('blog:index'))

    def test_moderator_can_create_post(self):
        self.client.force_login(self.moderator)
        res = self.client.post(self.url, {
            'topic': self.existing_topic.pk,
            'new_topic_title': '',
            'heading': 'Moderator Beitrag',
            'body': 'Inhalt vom Moderator',
            'tags': '',
        })
        self.assertRedirects(res, self.existing_topic.get_absolute_url())
        self.assertTrue(TopicPart.objects.filter(heading='Moderator Beitrag').exists())

    def test_moderator_can_create_new_topic_and_post(self):
        self.client.force_login(self.moderator)
        res = self.client.post(self.url, {
            'topic': '',
            'new_topic_title': 'Neues Moderator Thema',
            'heading': 'Erster Teil',
            'body': 'Text',
            'tags': '',
        })
        new_topic = Topic.objects.get(title='Neues Moderator Thema')
        self.assertRedirects(res, new_topic.get_absolute_url())


class ModeratorCommentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moderator = User.objects.create_user(
            email='mod@example.com', name='Mod User', password='pw',
        )
        cls.moderator.groups.add(_get_moderator_group())
        cls.author = User.objects.create_user(
            email='author@example.com', name='Author User', password='pw',
        )
        cls.topic = Topic.objects.create(
            title='Kommentar Thema', author=cls.author, is_published=True,
        )
        cls.detail_url = reverse('blog:topic_detail', kwargs={'slug': cls.topic.slug})

    def setUp(self):
        self.comment = Comment.objects.create(
            topic=self.topic, author=self.author, body='Ein Kommentar'
        )

    def _delete_url(self):
        return reverse('blog:comment_delete', kwargs={
            'slug': self.topic.slug,
            'pk': self.comment.pk,
        })

    def test_moderator_can_add_comment(self):
        self.client.force_login(self.moderator)
        res = self.client.post(self.detail_url, {'body': 'Moderator Kommentar'})
        self.assertRedirects(res, self.detail_url)
        self.assertTrue(Comment.objects.filter(body='Moderator Kommentar').exists())

    def test_moderator_can_delete_comment(self):
        self.client.force_login(self.moderator)
        res = self.client.post(self._delete_url())
        self.assertRedirects(res, self.detail_url)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_regular_user_cannot_delete_comment(self):
        regular = User.objects.create_user(
            email='regular@example.com', name='Regular User', password='pw',
        )
        self.client.force_login(regular)
        res = self.client.post(self._delete_url())
        self.assertRedirects(res, reverse('blog:index'))
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_anonymous_cannot_delete_comment(self):
        res = self.client.post(self._delete_url())
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login/', res.url)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_delete_requires_post_method(self):
        self.client.force_login(self.moderator)
        res = self.client.get(self._delete_url())
        self.assertEqual(res.status_code, 405)

    def test_delete_nonexistent_comment_returns_404(self):
        self.client.force_login(self.moderator)
        url = reverse('blog:comment_delete', kwargs={
            'slug': self.topic.slug,
            'pk': 99999,
        })
        res = self.client.post(url)
        self.assertEqual(res.status_code, 404)

    def test_delete_button_visible_to_moderator(self):
        self.client.force_login(self.moderator)
        res = self.client.get(self.detail_url)
        expected = reverse('blog:comment_delete', kwargs={
            'slug': self.topic.slug, 'pk': self.comment.pk,
        })
        self.assertContains(res, expected)

    def test_delete_button_hidden_from_regular_user(self):
        regular = User.objects.create_user(
            email='regular2@example.com', name='Regular2 User', password='pw',
        )
        self.client.force_login(regular)
        res = self.client.get(self.detail_url)
        expected = reverse('blog:comment_delete', kwargs={
            'slug': self.topic.slug, 'pk': self.comment.pk,
        })
        self.assertNotContains(res, expected)


class ModeratorGroupSetupTests(TestCase):
    def test_moderator_group_has_required_permissions(self):
        group = _get_moderator_group()
        codenames = set(group.permissions.values_list('codename', flat=True))
        self.assertIn('add_topicpart', codenames)
        self.assertIn('add_comment', codenames)
        self.assertIn('delete_comment', codenames)
