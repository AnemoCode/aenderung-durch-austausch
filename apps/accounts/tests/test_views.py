from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegisterViewTests(TestCase):
    url = None

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('accounts:register')

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_authenticated_user_redirected_to_blog(self):
        user = User.objects.create_user(email='a@example.com', name='A', password='pw123456!')
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('blog:index'))

    def test_valid_post_creates_user_and_redirects(self):
        response = self.client.post(self.url, {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertRedirects(response, reverse('blog:index'))
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_valid_post_logs_user_in(self):
        self.client.post(self.url, {
            'name': 'Auto Login User',
            'email': 'autologin@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        response = self.client.get(reverse('blog:index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_post_rerenders_form(self):
        response = self.client.post(self.url, {
            'name': '',
            'email': 'bad',
            'password1': 'pw',
            'password2': 'pw',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='bad').exists())

    def test_mismatching_passwords_rerenders_form(self):
        response = self.client.post(self.url, {
            'name': 'Test',
            'email': 'mismatch@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='mismatch@example.com').exists())
