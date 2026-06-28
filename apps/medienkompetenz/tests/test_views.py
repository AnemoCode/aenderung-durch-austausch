import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.medienkompetenz.models import Article, InteractiveBlock, UploadedImage

User = get_user_model()


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new('RGB', (4, 4), color=(255, 0, 0)).save(buffer, format='PNG')
    return buffer.getvalue()


_TMP_MEDIA = tempfile.mkdtemp(prefix='mk-media-')


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class ArticleViewsTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.staff = User.objects.create_user(
            email='staff@example.com', name='Staff', password='pw1234567890',
        )
        self.staff.is_staff = True
        self.staff.save()
        self.reader = User.objects.create_user(
            email='reader@example.com', name='Reader', password='pw1234567890',
        )
        self.article = Article.objects.create(
            title='KI-Bilder erkennen',
            body='<p>Inhalt</p>',
            author=self.staff,
        )

    def test_list_is_public(self):
        resp = self.client.get(reverse('medienkompetenz:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'KI-Bilder erkennen')

    def test_detail_is_public(self):
        resp = self.client.get(self.article.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Inhalt')

    def test_unpublished_article_404s(self):
        self.article.is_published = False
        self.article.save()
        resp = self.client.get(self.article.get_absolute_url())
        self.assertEqual(resp.status_code, 404)

    def test_create_requires_perm(self):
        self.client.force_login(self.reader)
        resp = self.client.get(reverse('medienkompetenz:create'))
        self.assertRedirects(resp, reverse('medienkompetenz:index'))

    def test_staff_can_create_article(self):
        self.client.force_login(self.staff)
        resp = self.client.post(reverse('medienkompetenz:create'), data={
            'title': 'Bot-Erkennung',
            'lead': 'Kurzer Lead',
            'body': '<p>Body</p>',
            'references': '',
            'is_published': 'on',
            'tags': 'bots, social',
        })
        self.assertEqual(resp.status_code, 302)
        article = Article.objects.get(title='Bot-Erkennung')
        self.assertEqual({t.name for t in article.tags.all()}, {'bots', 'social'})


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class BlockViewsTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.staff = User.objects.create_user(
            email='staff2@example.com', name='Staff2', password='pw1234567890',
        )
        self.staff.is_staff = True
        self.staff.save()
        self.article = Article.objects.create(title='Test', body='<p>x</p>', author=self.staff)
        self.client.force_login(self.staff)

    def test_create_text_callout_block(self):
        url = reverse(
            'medienkompetenz:block_create',
            kwargs={'slug': self.article.slug, 'block_type': 'text_callout'},
        )
        resp = self.client.post(url, data={
            'title': 'Tipp',
            'instructions': '',
            'tone': 'tip',
            'body': '<p>Schau auf die Augen.</p>',
        })
        self.assertEqual(resp.status_code, 302)
        block = InteractiveBlock.objects.get(article=self.article)
        self.assertEqual(block.block_type, 'text_callout')
        self.assertEqual(block.data['tone'], 'tip')
        self.assertIn('Augen', block.data['body'])

    def test_unknown_block_type_redirects(self):
        url = reverse(
            'medienkompetenz:block_create',
            kwargs={'slug': self.article.slug, 'block_type': 'bogus'},
        )
        resp = self.client.get(url)
        self.assertRedirects(resp, reverse('medienkompetenz:edit', kwargs={'slug': self.article.slug}))


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class ImageUploadTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.staff = User.objects.create_user(
            email='upload@example.com', name='Up', password='pw1234567890',
        )
        self.staff.is_staff = True
        self.staff.save()

    def test_upload_requires_auth(self):
        resp = self.client.post(reverse('medienkompetenz:image_upload'))
        self.assertEqual(resp.status_code, 401)

    def test_uploads_png_and_returns_url(self):
        self.client.force_login(self.staff)
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile('p.png', _png_bytes(), content_type='image/png')
        resp = self.client.post(reverse('medienkompetenz:image_upload'), data={'image': upload})
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertIn('url', body)
        self.assertTrue(UploadedImage.objects.filter(pk=body['id']).exists())

    def test_rejects_non_image_content_type(self):
        self.client.force_login(self.staff)
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile('p.txt', b'plain text', content_type='text/plain')
        resp = self.client.post(reverse('medienkompetenz:image_upload'), data={'image': upload})
        self.assertEqual(resp.status_code, 400)
