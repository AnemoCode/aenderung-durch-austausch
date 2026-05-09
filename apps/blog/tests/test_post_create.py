from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Topic, TopicPart

User = get_user_model()


class PostCreateViewTests(TestCase):
    url = None

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('blog:post_create')
        cls.staff = User.objects.create_user(
            email='staff@example.com', name='Staff User', password='pw',
        )
        cls.staff.is_staff = True
        cls.staff.save()
        cls.other = User.objects.create_user(
            email='other@example.com', name='Other User', password='pw',
        )
        cls.existing_topic = Topic.objects.create(
            title='Mobilität', author=cls.other, is_published=True,
        )
        TopicPart.objects.create(
            topic=cls.existing_topic, author=cls.other,
            heading='Erster Teil', body='…', order=0,
        )

    def test_anonymous_redirects_to_login(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login/', res.url)

    def test_non_staff_redirects_to_index(self):
        self.client.force_login(self.other)
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('blog:index'))

    def test_staff_can_get_form(self):
        self.client.force_login(self.staff)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Neuer Beitrag')

    def test_post_to_existing_topic_creates_part_with_author_and_order(self):
        self.client.force_login(self.staff)
        res = self.client.post(self.url, {
            'topic': self.existing_topic.pk,
            'new_topic_title': '',
            'heading': 'Zweiter Teil',
            'body': 'Text',
            'tags': '',
        })
        self.assertRedirects(res, self.existing_topic.get_absolute_url())
        part = TopicPart.objects.get(heading='Zweiter Teil')
        self.assertEqual(part.author, self.staff)
        self.assertEqual(part.topic, self.existing_topic)
        self.assertEqual(part.order, 1)

    def test_post_with_new_title_creates_topic_and_part(self):
        self.client.force_login(self.staff)
        res = self.client.post(self.url, {
            'topic': '',
            'new_topic_title': 'Neues Thema',
            'heading': 'Kopfzeile',
            'body': 'Inhalt',
            'tags': 'klima, energie',
        })
        new_topic = Topic.objects.get(title='Neues Thema')
        self.assertEqual(new_topic.author, self.staff)
        self.assertTrue(new_topic.is_published)
        self.assertRedirects(res, new_topic.get_absolute_url())
        part = new_topic.parts.get()
        self.assertEqual(part.author, self.staff)
        self.assertEqual(part.order, 0)
        self.assertCountEqual(
            list(part.tags.values_list('name', flat=True)), ['klima', 'energie'],
        )

    def test_both_topic_and_new_title_is_rejected(self):
        self.client.force_login(self.staff)
        res = self.client.post(self.url, {
            'topic': self.existing_topic.pk,
            'new_topic_title': 'Doppelt',
            'heading': 'X',
            'body': 'Y',
            'tags': '',
        })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Topic.objects.filter(title='Doppelt').exists())

    def test_neither_topic_nor_title_is_rejected(self):
        self.client.force_login(self.staff)
        res = self.client.post(self.url, {
            'topic': '',
            'new_topic_title': '',
            'heading': 'X',
            'body': 'Y',
            'tags': '',
        })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(TopicPart.objects.filter(heading='X').exists())

    def test_duplicate_new_title_is_rejected_case_insensitive(self):
        self.client.force_login(self.staff)
        res = self.client.post(self.url, {
            'topic': '',
            'new_topic_title': 'mobilität',
            'heading': 'Kopfzeile',
            'body': 'Inhalt',
            'tags': '',
        })
        self.assertEqual(res.status_code, 200)
        # Only the one existing topic, no duplicate created
        self.assertEqual(Topic.objects.filter(title__iexact='mobilität').count(), 1)

    def test_quill_submit_handler_targets_post_form_not_logout(self):
        # The Quill JS copies the editor HTML into the hidden body input on
        # form submit. The page contains a logout form in the header, so the
        # handler must target the post form by id — not the first form on the
        # page — otherwise the submit fires without copying the editor content.
        self.client.force_login(self.staff)
        res = self.client.get(self.url)
        self.assertContains(res, 'id="post-form"')
        self.assertContains(res, "getElementById('post-form').addEventListener")
        self.assertNotContains(res, "querySelector('form').addEventListener")

    def test_body_value_persists_on_validation_error(self):
        self.client.force_login(self.staff)
        body_html = '<p>Hello <strong>world</strong></p>'
        res = self.client.post(self.url, {
            'topic': '',
            'new_topic_title': '',  # missing — triggers validation error
            'heading': 'X',
            'body': body_html,
            'tags': '',
        })
        self.assertEqual(res.status_code, 200)
        # The hidden input must carry the submitted HTML back so the editor
        # can repopulate. Django auto-escapes the value attribute.
        self.assertContains(res, 'name="body"')
        self.assertContains(
            res,
            'value="&lt;p&gt;Hello &lt;strong&gt;world&lt;/strong&gt;&lt;/p&gt;"',
        )
