from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Titel'))
    subtitle = models.CharField(max_length=300, blank=True, verbose_name=_('Untertitel'))
    description = models.TextField(verbose_name=_('Inhalt'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name=_('Veröffentlicht'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Beitrag')
        verbose_name_plural = _('Beiträge')

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
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
        return f'{self.author.name} → {self.post.title}'


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('post', 'user')]
        verbose_name = _('Gefällt mir')
        verbose_name_plural = _('Gefällt mir')

    def __str__(self):
        return f'{self.user.name} → {self.post.title}'
