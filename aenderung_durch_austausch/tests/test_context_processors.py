from django.test import TestCase, override_settings
from django.urls import reverse


class StagingContextProcessorTests(TestCase):
    def test_staging_false_returns_empty_context(self):
        with override_settings(STAGING=False):
            response = self.client.get(reverse('landing'))
        self.assertNotIn('staging_credentials', response.context)

    def test_staging_true_injects_credentials(self):
        with override_settings(STAGING=True):
            response = self.client.get(reverse('landing'))
        self.assertIn('staging_credentials', response.context)
        creds = response.context['staging_credentials']
        self.assertIsInstance(creds, list)
        self.assertGreater(len(creds), 0)


class HealthCheckViewTests(TestCase):
    def test_health_returns_ok(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')


class LandingPageTests(TestCase):
    def test_landing_returns_200(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)


class PillarPageTests(TestCase):
    def test_argumentation_page_returns_200(self):
        response = self.client.get(reverse('argumentation'))
        self.assertEqual(response.status_code, 200)

    def test_medienkompetenz_page_returns_200(self):
        response = self.client.get(reverse('medienkompetenz'))
        self.assertEqual(response.status_code, 200)

    def test_kommunikation_page_returns_200(self):
        response = self.client.get(reverse('kommunikation'))
        self.assertEqual(response.status_code, 200)
