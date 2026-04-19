from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_normalises_email(self):
        user = User.objects.create_user(email='Test@EXAMPLE.COM', name='Alice', password='pw')
        self.assertEqual(user.email, 'Test@example.com')

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', name='Alice', password='pw')

    def test_create_user_defaults(self):
        user = User.objects.create_user(email='a@example.com', name='A', password='pw')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_flags(self):
        user = User.objects.create_superuser(email='su@example.com', name='SU', password='pw')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_no_password_sets_unusable(self):
        user = User.objects.create_user(email='nopw@example.com', name='NoPw')
        self.assertFalse(user.has_usable_password())


class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='john.doe@example.com', name='John Doe', password='secret'
        )

    def test_str_returns_email(self):
        self.assertEqual(str(self.user), 'john.doe@example.com')

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'John Doe')

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), 'John Doe')

    def test_initials_two_words(self):
        self.assertEqual(self.user.initials, 'JD')

    def test_initials_single_word(self):
        user = User.objects.create_user(email='mono@example.com', name='Madonna', password='pw')
        self.assertEqual(user.initials, 'MA')

    def test_initials_more_than_two_words_uses_first_and_last(self):
        user = User.objects.create_user(
            email='multi@example.com', name='Anna Maria Schmidt', password='pw'
        )
        self.assertEqual(user.initials, 'AS')

    def test_initials_uppercased(self):
        user = User.objects.create_user(email='lc@example.com', name='anna becker', password='pw')
        self.assertEqual(user.initials, 'AB')

    def test_date_joined_set_on_creation(self):
        self.assertIsNotNone(self.user.date_joined)

    def test_username_field_is_email(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_required_fields_include_name(self):
        self.assertIn('name', User.REQUIRED_FIELDS)
