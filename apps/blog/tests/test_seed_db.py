from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from apps.blog.models import Comment, Like, Topic, TopicPart
from apps.definitions.models import Definition

User = get_user_model()


class SeedDbCommandTests(TestCase):
    def test_seed_creates_users(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        self.assertTrue(User.objects.filter(email='admin@staging.local').exists())
        self.assertTrue(User.objects.filter(email='alice@staging.local').exists())
        self.assertTrue(User.objects.filter(email='bob@staging.local').exists())

    def test_seed_creates_admin_as_staff_superuser(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        admin = User.objects.get(email='admin@staging.local')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_seed_creates_topics(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        self.assertTrue(Topic.objects.filter(title='Klimawandel und städtische Mobilität').exists())
        self.assertTrue(Topic.objects.filter(title='Digitale Bildung in Schulen').exists())
        self.assertTrue(Topic.objects.filter(title='Zukunft der Arbeit: Remote-Work-Modelle').exists())

    def test_seed_creates_topic_parts(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        self.assertGreater(TopicPart.objects.count(), 0)

    def test_seed_creates_comments(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        self.assertGreater(Comment.objects.count(), 0)

    def test_seed_creates_likes(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        self.assertGreater(Like.objects.count(), 0)

    def test_seed_creates_definitions(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        self.assertTrue(Definition.objects.filter(term='Verschwörungstheorie').exists())

    def test_seed_assigns_alice_to_moderator_group(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        alice = User.objects.get(email='alice@staging.local')
        self.assertTrue(alice.groups.filter(name='Moderator').exists())

    def test_seed_is_idempotent(self):
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        call_command('seed_db', stdout=StringIO(), stderr=StringIO())
        self.assertEqual(User.objects.filter(email='admin@staging.local').count(), 1)
        self.assertEqual(Topic.objects.filter(title='Klimawandel und städtische Mobilität').count(), 1)

    def test_seed_with_flush_clears_data(self):
        User.objects.create_user(email='existing@example.com', name='Existing', password='pw')
        initial_count = User.objects.count()
        self.assertGreater(initial_count, 0)
        call_command('seed_db', flush=True, stdout=StringIO(), stderr=StringIO())
        self.assertFalse(User.objects.filter(email='existing@example.com').exists())

    def test_seed_without_moderator_group_skips_gracefully(self):
        Group.objects.filter(name='Moderator').delete()
        stdout = StringIO()
        call_command('seed_db', stdout=stdout, stderr=StringIO())
        self.assertTrue(User.objects.filter(email='admin@staging.local').exists())
