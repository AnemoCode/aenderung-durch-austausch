from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Topic(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Titel'))
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name=_('URL-Kürzel'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name=_('Autor'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False, verbose_name=_('Veröffentlicht'))
    legacy_post_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        editable=False,
        help_text='PK des migrierten MVP-Posts (für Redirect-Backwards-Compat).',
    )
    tags = TaggableManager(blank=True, verbose_name=_('Tags'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Thema')
        verbose_name_plural = _('Themen')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:topic_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=False) or 'thema'
            slug = base
            counter = 1
            while Topic.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class TopicPart(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='parts',
        verbose_name=_('Thema'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topic_parts',
        verbose_name=_('Autor'),
    )
    heading = models.CharField(max_length=300, verbose_name=_('Unterüberschrift'))
    body = models.TextField(verbose_name=_('Inhalt'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Reihenfolge'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True, verbose_name=_('Tags'))

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = _('Thementeil')
        verbose_name_plural = _('Thementeile')

    def __str__(self):
        return f'{self.topic.title} — {self.heading}'


class Comment(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    body = models.TextField(verbose_name=_('Kommentar'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Kommentar')
        verbose_name_plural = _('Kommentare')

    def __str__(self):
        return f'{self.author.name} → {self.topic.title}'


class Like(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('topic', 'user')]
        verbose_name = _('Gefällt mir')
        verbose_name_plural = _('Gefällt mir')

    def __str__(self):
        return f'{self.user.name} → {self.topic.title}'
