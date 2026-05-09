from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Topic, TopicPart

User = get_user_model()


class TopicPartUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            email="staff@example.com",
            name="Staff User",
            password="pw",
        )
        cls.staff.is_staff = True
        cls.staff.save()

        cls.other = User.objects.create_user(
            email="other@example.com",
            name="Other User",
            password="pw",
        )

        cls.topic = Topic.objects.create(
            title="Klimawandel",
            author=cls.staff,
            is_published=True,
        )
        cls.part = TopicPart.objects.create(
            topic=cls.topic,
            author=cls.staff,
            heading="Ursprüngliche Überschrift",
            body="Ursprünglicher Inhalt",
            order=0,
        )
        cls.part.tags.add("klima")
        cls.url = reverse("blog:post_edit", kwargs={"pk": cls.part.pk})

    def test_anonymous_redirects_to_login(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login/", res.url)

    def test_non_staff_redirects_to_index(self):
        self.client.force_login(self.other)
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse("blog:index"))

    def test_staff_can_get_edit_form(self):
        self.client.force_login(self.staff)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Beitrag bearbeiten")

    def test_form_is_prepopulated_with_existing_data(self):
        self.client.force_login(self.staff)
        res = self.client.get(self.url)
        self.assertContains(res, "Ursprüngliche Überschrift")
        self.assertContains(res, "Ursprünglicher Inhalt")

    def test_staff_can_edit_part(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            self.url,
            {
                "heading": "Neue Überschrift",
                "body": "Neuer Inhalt",
                "tags": "energie",
            },
        )
        self.assertRedirects(res, self.topic.get_absolute_url())
        self.part.refresh_from_db()
        self.assertEqual(self.part.heading, "Neue Überschrift")
        self.assertEqual(self.part.body, "Neuer Inhalt")

    def test_edit_updates_tags(self):
        self.client.force_login(self.staff)
        self.client.post(
            self.url,
            {
                "heading": "Überschrift",
                "body": "Inhalt",
                "tags": "energie, mobilitaet",
            },
        )
        self.part.refresh_from_db()
        tag_names = set(self.part.tags.values_list("name", flat=True))
        self.assertEqual(tag_names, {"energie", "mobilitaet"})

    def test_edit_clears_tags_when_empty(self):
        self.client.force_login(self.staff)
        self.client.post(
            self.url,
            {
                "heading": "Überschrift",
                "body": "Inhalt",
                "tags": "",
            },
        )
        self.part.refresh_from_db()
        self.assertEqual(self.part.tags.count(), 0)

    def test_empty_heading_shows_form_error(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            self.url,
            {
                "heading": "",
                "body": "Inhalt",
                "tags": "",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.part.refresh_from_db()
        self.assertEqual(self.part.heading, "Ursprüngliche Überschrift")

    def test_nonexistent_part_returns_404(self):
        self.client.force_login(self.staff)
        url = reverse("blog:post_edit", kwargs={"pk": 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)
