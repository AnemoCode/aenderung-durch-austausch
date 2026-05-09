import bleach
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Topic, TopicPart

ALLOWED_TAGS = ['h2', 'h3', 'p', 'ul', 'ol', 'li', 'a', 'strong', 'em', 'blockquote', 'br']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title', 'rel']}


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description']
        labels = {
            'title': _('Titel'),
            'description': _('Beschreibung'),
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class TopicPartForm(forms.ModelForm):
    class Meta:
        model = TopicPart
        fields = ['title', 'body', 'order']
        labels = {
            'title': _('Titel'),
            'body': _('Inhalt'),
            'order': _('Reihenfolge'),
        }
        widgets = {
            # Hidden input: JavaScript writes Quill HTML here before submit
            'body': forms.HiddenInput(attrs={'id': 'id_body'}),
        }

    def clean_body(self):
        raw = self.cleaned_data.get('body', '')
        sanitized = bleach.clean(
            raw,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
        )
        return sanitized
