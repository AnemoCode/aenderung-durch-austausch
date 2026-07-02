import tempfile

from django.test import TestCase, override_settings


class MediaServingTests(TestCase):
    """User-uploaded media must be served in every environment.

    Production runs with DEBUG=False, where Django historically only added the
    /media/ route under `if settings.DEBUG`.  That made images 404 in prod even
    though they served fine in staging (which runs DEBUG=True).  These tests
    pin the production behaviour so the regression cannot come back.
    """

    def _write_media_file(self, media_root, name=b"hello media"):
        import os

        path = os.path.join(media_root, "sample.txt")
        with open(path, "wb") as fh:
            fh.write(name)
        return path

    def test_media_served_when_debug_false(self):
        with tempfile.TemporaryDirectory() as media_root:
            self._write_media_file(media_root)
            with override_settings(DEBUG=False, MEDIA_ROOT=media_root):
                response = self.client.get("/media/sample.txt")
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content) if response.streaming else response.content
        self.assertEqual(body, b"hello media")

    def test_media_served_when_debug_true(self):
        with tempfile.TemporaryDirectory() as media_root:
            self._write_media_file(media_root)
            with override_settings(DEBUG=True, MEDIA_ROOT=media_root):
                response = self.client.get("/media/sample.txt")
        self.assertEqual(response.status_code, 200)

    def test_missing_media_returns_404(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(DEBUG=False, MEDIA_ROOT=media_root):
                response = self.client.get("/media/does-not-exist.png")
        self.assertEqual(response.status_code, 404)
