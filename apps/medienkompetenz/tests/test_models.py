from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.medienkompetenz.models import Article, InteractiveBlock

User = get_user_model()


class ArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='author@example.com',
            name='Author',
            password='pw1234567890',
        )

    def test_str_returns_title(self):
        a = Article(title='Bilder erkennen', body='<p>x</p>')
        self.assertEqual(str(a), 'Bilder erkennen')

    def test_slug_is_auto_generated(self):
        a = Article.objects.create(
            title='Wie KI-Bilder erkannt werden',
            body='<p>x</p>',
            author=self.user,
        )
        self.assertEqual(a.slug, 'wie-ki-bilder-erkannt-werden')

    def test_slug_uniqueness_is_enforced_by_counter(self):
        Article.objects.create(title='Framing', body='<p>x</p>', author=self.user)
        second = Article.objects.create(title='Framing', body='<p>y</p>', author=self.user)
        self.assertEqual(second.slug, 'framing-1')

    def test_absolute_url_uses_slug(self):
        a = Article.objects.create(title='Bots', body='<p>x</p>', author=self.user)
        self.assertEqual(a.get_absolute_url(), f'/medienkompetenz/{a.slug}/')


class InteractiveBlockTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='u@example.com', name='U', password='pw1234567890',
        )
        self.article = Article.objects.create(title='Bot-Erkennung', body='<p>x</p>', author=self.user)

    def test_template_name_matches_type(self):
        b = InteractiveBlock(
            article=self.article,
            block_type=InteractiveBlock.BlockType.AI_IMAGE_QUIZ,
        )
        self.assertEqual(b.template_name, 'medienkompetenz/blocks/_ai_image_quiz.html')

    def test_str_falls_back_to_type_label_when_title_blank(self):
        b = InteractiveBlock.objects.create(
            article=self.article,
            block_type=InteractiveBlock.BlockType.FRAMING_EXERCISE,
        )
        self.assertIn('Framing', str(b))
