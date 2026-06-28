from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_normalises_email(self):
        user = User.objects.create_user(email='Test@Example.COM', name='Test', password='pw123456!')
        self.assertEqual(user.email, 'Test@example.com')

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', name='Name', password='pw')

    def test_create_superuser_sets_flags(self):
        user = User.objects.create_superuser(email='admin@example.com', name='Admin', password='pw123456!')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_can_override_flags(self):
        user = User.objects.create_superuser(
            email='admin2@example.com', name='Admin2', password='pw123456!',
            is_staff=True, is_superuser=True,
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='john.doe@example.com', name='John Doe', password='pw123456!',
        )

    def test_str_returns_email(self):
        self.assertEqual(str(self.user), 'john.doe@example.com')

    def test_get_full_name_returns_name(self):
        self.assertEqual(self.user.get_full_name(), 'John Doe')

    def test_get_short_name_returns_name(self):
        self.assertEqual(self.user.get_short_name(), 'John Doe')

    def test_initials_two_words(self):
        self.assertEqual(self.user.initials, 'JD')

    def test_initials_single_word(self):
        user = User(name='Alice')
        self.assertEqual(user.initials, 'AL')

    def test_initials_three_words_uses_first_and_last(self):
        user = User(name='Maria Anna Schmidt')
        self.assertEqual(user.initials, 'MS')

    def test_is_active_defaults_true(self):
        self.assertTrue(self.user.is_active)

    def test_is_staff_defaults_false(self):
        self.assertFalse(self.user.is_staff)
