from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ProfileViewTests(TestCase):
    url = None

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('accounts:profile')

    def setUp(self):
        self.user = User.objects.create_user(
            email='jana@example.org',
            name='Jana Demir',
            password='OldPass123!',
        )
        self.client.force_login(self.user)

    def test_unauthenticated_user_is_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    def test_get_renders_profile_with_user_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jana Demir')
        self.assertContains(response, 'jana@example.org')

    def test_profile_post_updates_name_and_email(self):
        response = self.client.post(self.url, {
            'form_type': 'profile',
            'name': 'Jana Neu',
            'email': 'jana.neu@example.org',
        })
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Jana Neu')
        self.assertEqual(self.user.email, 'jana.neu@example.org')

    def test_profile_post_with_duplicate_email_shows_error(self):
        User.objects.create_user(
            email='taken@example.org', name='Other', password='pw123456!'
        )
        response = self.client.post(self.url, {
            'form_type': 'profile',
            'name': 'Jana Demir',
            'email': 'taken@example.org',
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'jana@example.org')

    def test_password_post_changes_password_and_keeps_session(self):
        response = self.client.post(self.url, {
            'form_type': 'password',
            'old_password': 'OldPass123!',
            'new_password1': 'BrandNewPass456!',
            'new_password2': 'BrandNewPass456!',
        })
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BrandNewPass456!'))
        # Session is preserved via update_session_auth_hash.
        follow_up = self.client.get(self.url)
        self.assertEqual(follow_up.status_code, 200)
        self.assertTrue(follow_up.wsgi_request.user.is_authenticated)

    def test_password_post_with_wrong_old_password_shows_error(self):
        response = self.client.post(self.url, {
            'form_type': 'password',
            'old_password': 'WrongPass000!',
            'new_password1': 'BrandNewPass456!',
            'new_password2': 'BrandNewPass456!',
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPass123!'))

    def test_header_shows_profile_link_when_logged_in(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.url)
        self.assertContains(response, 'Mein Profil')
