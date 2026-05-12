from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


def _article_hero_upload_to(instance, filename):
    return f'medienkompetenz/hero/{filename}'


def _block_image_upload_to(instance, filename):
    return f'medienkompetenz/blocks/{filename}'


class Article(models.Model):
    """A media-literacy article. Combines a Quill rich-text body with one or
    more InteractiveBlocks that the reader works through inline."""

    title = models.CharField(max_length=200, verbose_name=_('Titel'))
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name=_('URL-Kürzel'),
    )
    lead = models.CharField(
        max_length=400,
        blank=True,
        default='',
        verbose_name=_('Einleitung'),
        help_text=_('Kurzer Lead-Text unter dem Titel.'),
    )
    body = models.TextField(
        verbose_name=_('Inhalt'),
        help_text=_('Reichtext-Inhalt (Quill). Bilder und Videos können eingebettet werden.'),
    )
    references = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Quellenangaben & Verweise'),
        help_text=_('Literatur, Links und Quellenangaben zu diesem Beitrag.'),
    )
    hero_image = models.ImageField(
        upload_to=_article_hero_upload_to,
        blank=True,
        null=True,
        verbose_name=_('Titelbild'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medienkompetenz_articles',
        verbose_name=_('Autor'),
    )
    is_published = models.BooleanField(default=True, verbose_name=_('Veröffentlicht'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True, verbose_name=_('Tags'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Medienkompetenz-Beitrag')
        verbose_name_plural = _('Medienkompetenz-Beiträge')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('medienkompetenz:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=False) or 'beitrag'
            slug = base
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class InteractiveBlock(models.Model):
    """An interactive section embedded in an Article — e.g. an AI-image-quiz
    or a framing exercise. The block_type drives which template renders it and
    which schema lives in `data`."""

    class BlockType(models.TextChoices):
        AI_IMAGE_QUIZ = 'ai_image_quiz', _('KI-Bild-Quiz')
        FRAMING_EXERCISE = 'framing_exercise', _('Framing-Übung')
        TEXT_CALLOUT = 'text_callout', _('Hervorhebung')

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='blocks',
        verbose_name=_('Beitrag'),
    )
    block_type = models.CharField(
        max_length=32,
        choices=BlockType.choices,
        verbose_name=_('Typ'),
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name=_('Titel'),
    )
    instructions = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Anleitung'),
        help_text=_('Erklärung für die Leser:innen – wird über den interaktiven Inhalten angezeigt.'),
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Konfiguration'),
        help_text=_('Typ-spezifische Daten (Fragen, Optionen, Bild-Pfade, …).'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Reihenfolge'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = _('Interaktiver Abschnitt')
        verbose_name_plural = _('Interaktive Abschnitte')

    def __str__(self):
        label = self.title or self.get_block_type_display()
        return f'{self.article.title} — {label}'

    @property
    def template_name(self) -> str:
        return f'medienkompetenz/blocks/_{self.block_type}.html'


class UploadedImage(models.Model):
    """Tracks images uploaded inline via the Quill image button. Storing a
    record makes it possible to attribute uploads, list them in admin, and
    later prune orphans."""

    file = models.ImageField(upload_to=_block_image_upload_to, verbose_name=_('Datei'))
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medienkompetenz_uploads',
        verbose_name=_('Hochgeladen von'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Hochgeladenes Bild')
        verbose_name_plural = _('Hochgeladene Bilder')

    def __str__(self):
        return self.file.name
