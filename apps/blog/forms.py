from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'subtitle', 'description']
        labels = {
            'title': _('Titel'),
            'subtitle': _('Untertitel'),
            'description': _('Inhalt'),
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 12}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        labels = {
            'body': _('Dein Kommentar'),
        }
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Schreibe einen Kommentar…')}),
        }
