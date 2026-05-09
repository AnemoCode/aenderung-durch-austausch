from django.test import TestCase

from .forms import TopicPartForm


class TopicPartFormSanitizationTest(TestCase):
    """Ensure Bleach strips disallowed tags and XSS vectors from body input."""

    def _submit_body(self, html):
        form = TopicPartForm(data={'title': 'Test', 'body': html, 'order': 0})
        self.assertTrue(form.is_valid(), form.errors)
        return form.cleaned_data['body']

    def test_allowed_tags_pass_through(self):
        html = '<h2>Heading</h2><p><strong>Bold</strong> and <em>italic</em></p>'
        result = self._submit_body(html)
        self.assertIn('<h2>', result)
        self.assertIn('<strong>', result)
        self.assertIn('<em>', result)

    def test_lists_pass_through(self):
        html = '<ul><li>Item 1</li><li>Item 2</li></ul>'
        result = self._submit_body(html)
        self.assertIn('<ul>', result)
        self.assertIn('<li>', result)

    def test_ordered_list_passes_through(self):
        html = '<ol><li>Step 1</li></ol>'
        result = self._submit_body(html)
        self.assertIn('<ol>', result)

    def test_blockquote_passes_through(self):
        html = '<blockquote>A quote</blockquote>'
        result = self._submit_body(html)
        self.assertIn('<blockquote>', result)

    def test_link_passes_through(self):
        html = '<p><a href="https://example.com" rel="noopener">Link</a></p>'
        result = self._submit_body(html)
        self.assertIn('<a ', result)
        self.assertIn('href=', result)

    # --- XSS tests ---

    def test_script_tag_stripped(self):
        result = self._submit_body('<script>alert(1)</script>')
        self.assertNotIn('<script>', result)
        self.assertNotIn('alert(1)', result)

    def test_script_tag_with_content_stripped(self):
        result = self._submit_body('<p>Hello</p><script>alert("xss")</script>')
        self.assertNotIn('<script>', result)
        self.assertNotIn('alert', result)
        self.assertIn('<p>Hello</p>', result)

    def test_inline_event_handler_stripped(self):
        result = self._submit_body('<p onclick="alert(1)">Click me</p>')
        self.assertNotIn('onclick', result)
        self.assertIn('Click me', result)

    def test_javascript_href_stripped(self):
        result = self._submit_body('<a href="javascript:alert(1)">Click</a>')
        self.assertNotIn('javascript:', result)

    def test_img_tag_stripped(self):
        # img is NOT in the allowed tags for B1 (only active from B3)
        result = self._submit_body('<img src="x" onerror="alert(1)">')
        self.assertNotIn('<img', result)

    def test_iframe_stripped(self):
        result = self._submit_body('<iframe src="https://evil.com"></iframe>')
        self.assertNotIn('<iframe>', result)
        self.assertNotIn('<iframe', result)

    def test_style_attribute_stripped(self):
        result = self._submit_body('<p style="background:url(javascript:alert(1))">text</p>')
        self.assertNotIn('style=', result)
        self.assertIn('text', result)

    def test_disallowed_tag_content_preserved(self):
        # Text inside disallowed tags should survive (strip=True removes tag, keeps text)
        result = self._submit_body('<div>Safe text</div>')
        self.assertNotIn('<div>', result)
        self.assertIn('Safe text', result)
