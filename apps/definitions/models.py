from django.conf import settings
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Definition(models.Model):
    term = models.CharField(max_length=200, verbose_name=_('Begriff'))
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name=_('URL-Kürzel'),
    )
    simple_explanation = models.TextField(
        verbose_name=_('Erklärung in einfacher Sprache'),
        help_text=_('Für alle verständlich — kurze Sätze, keine Fachbegriffe.'),
    )
    formal_explanation = models.TextField(
        verbose_name=_('Formale Definition'),
        help_text=_('Präzise, akademisch, mit Fachbegriffen wo nötig.'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='definitions',
        verbose_name=_('Autor'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name=_('Veröffentlicht'))
    references = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Quellenangaben & Verweise'),
        help_text=_('Literatur, Links und Quellenangaben zu dieser Definition.'),
    )
    tags = TaggableManager(blank=True, verbose_name=_('Tags'))

    class Meta:
        ordering = ['term']
        verbose_name = _('Definition')
        verbose_name_plural = _('Definitionen')
        constraints = [
            # Enforce case-insensitive uniqueness at the DB layer so the
            # invariant holds regardless of entry point (admin, ORM, racing
            # form submissions) — the form-level `clean_term` check alone is
            # not sufficient.
            models.UniqueConstraint(
                Lower('term'),
                name='definitions_definition_term_ci_unique',
            ),
        ]

    def __str__(self):
        return self.term

    def get_absolute_url(self):
        return reverse('definitions:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.term, allow_unicode=False) or 'begriff'
            slug = base
            counter = 1
            while Definition.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def initial_letter(self) -> str:
        """First uppercase letter for A–Z grouping; '#' for non-alphabetic starts."""
        if not self.term:
            return '#'
        first = self.term.strip()[:1].upper()
        # Fold German umlauts to their base letter so Ä sorts with A.
        umlauts = {'Ä': 'A', 'Ö': 'O', 'Ü': 'U', 'ẞ': 'S'}
        first = umlauts.get(first, first)
        return first if first.isalpha() and first.isascii() else '#'
