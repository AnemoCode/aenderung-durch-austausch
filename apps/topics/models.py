from django.db import models
from django.utils.translation import gettext_lazy as _


class Topic(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Titel'))
    description = models.TextField(blank=True, verbose_name=_('Beschreibung'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = _('Thema')
        verbose_name_plural = _('Themen')

    def __str__(self):
        return self.title


class TopicPart(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='parts')
    title = models.CharField(max_length=200, verbose_name=_('Titel'))
    body = models.TextField(verbose_name=_('Inhalt'))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_('Reihenfolge'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = _('Themanteil')
        verbose_name_plural = _('Thementeile')

    def __str__(self):
        return f'{self.topic.title} — {self.title}'
