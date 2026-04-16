from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment


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
