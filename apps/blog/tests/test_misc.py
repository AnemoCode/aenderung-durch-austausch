from django.test import TestCase, override_settings
from django.urls import reverse


class PillarPageTests(TestCase):
    def test_definitionen_returns_200(self):
        res = self.client.get('/definitionen/')
        self.assertEqual(res.status_code, 200)

    def test_argumentationsweisen_returns_200(self):
        res = self.client.get('/argumentationsweisen/')
        self.assertEqual(res.status_code, 200)

    def test_medienkompetenz_returns_200(self):
        res = self.client.get('/medienkompetenz/')
        self.assertEqual(res.status_code, 200)

    def test_kommunikationstechniken_returns_200(self):
        res = self.client.get('/kommunikationstechniken/')
        self.assertEqual(res.status_code, 200)


class StagingContextProcessorTests(TestCase):
    @override_settings(STAGING=False)
    def test_non_staging_returns_empty_dict(self):
        res = self.client.get(reverse('landing'))
        self.assertNotIn('staging_credentials', res.context)

    @override_settings(STAGING=True)
    def test_staging_injects_credentials(self):
        res = self.client.get(reverse('landing'))
        self.assertIn('staging_credentials', res.context)


class AccountsLoginViewTests(TestCase):
    def test_login_page_returns_200(self):
        res = self.client.get(reverse('accounts:login'))
        self.assertEqual(res.status_code, 200)

    def test_login_page_has_email_field(self):
        res = self.client.get(reverse('accounts:login'))
        self.assertContains(res, 'email')
