from django.test import TestCase, override_settings

# The production settings when someone turns on SECURE_SSL_REDIRECT.
SSL_REDIRECT = {
    'SECURE_SSL_REDIRECT': True,
    'SECURE_REDIRECT_EXEMPT': [r'^health/$'],
    'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
}


@override_settings(**SSL_REDIRECT)
class SslRedirectTests(TestCase):
    """The deploy workflow and the container healthcheck call /health/ over
    plain HTTP. If that got redirected, the health check would no longer test
    the app itself."""

    def test_health_check_is_not_redirected(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)

    def test_plain_http_page_is_redirected_to_https(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response['Location'].startswith('https://'))

    def test_request_marked_https_by_proxy_is_served(self):
        response = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(response.status_code, 200)


@override_settings(SECURE_HSTS_SECONDS=3600, SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
class HstsTests(TestCase):
    def test_hsts_header_sent_on_https(self):
        response = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertIn('max-age=3600', response['Strict-Transport-Security'])

    def test_no_hsts_header_on_plain_http(self):
        response = self.client.get('/')
        self.assertNotIn('Strict-Transport-Security', response)
