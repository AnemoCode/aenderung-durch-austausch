from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse('accounts:register')

    def test_get_renders_form(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('form', res.context)

    def test_authenticated_user_redirected_to_blog(self):
        user = User.objects.create_user(email='auth@example.com', name='Auth', password='pw')
        self.client.force_login(user)
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('blog:index'))

    def test_valid_registration_logs_in_and_redirects(self):
        res = self.client.post(self.url, {
            'name': 'New User',
            'email': 'new@example.com',
            'password1': 'str0ng!Passw0rd',
            'password2': 'str0ng!Passw0rd',
        })
        self.assertRedirects(res, reverse('blog:index'))
        self.assertTrue(User.objects.filter(email='new@example.com').exists())
        # User should be logged in
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_registration_re_renders_form(self):
        res = self.client.post(self.url, {
            'name': 'New User',
            'email': 'new@example.com',
            'password1': 'pw1',
            'password2': 'pw2',
        })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(email='new@example.com').exists())

    def test_post_with_empty_data_shows_errors(self):
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context['form'].errors)
