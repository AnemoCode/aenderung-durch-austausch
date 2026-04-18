from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Topic


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


class TopicPartCreateForm(forms.Form):
    """Single form that creates a TopicPart and optionally a new Topic."""

    topic = forms.ModelChoiceField(
        queryset=Topic.objects.all().order_by('title'),
        required=False,
        label=_('Bestehendes Thema'),
        empty_label=_('– Neues Thema anlegen –'),
    )
    new_topic_title = forms.CharField(
        max_length=200,
        required=False,
        label=_('Titel des neuen Themas'),
    )
    heading = forms.CharField(
        max_length=300,
        required=True,
        label=_('Unterüberschrift'),
    )
    body = forms.CharField(
        required=True,
        label=_('Inhalt'),
        widget=forms.Textarea(attrs={'rows': 12}),
    )
    tags = forms.CharField(
        required=False,
        label=_('Tags'),
        help_text=_('Kommagetrennt, z. B. "klima, mobilitaet"'),
    )

    def clean(self):
        cleaned = super().clean()
        topic = cleaned.get('topic')
        new_title = (cleaned.get('new_topic_title') or '').strip()

        if topic and new_title:
            raise forms.ValidationError(
                _('Wähle entweder ein bestehendes Thema oder lege ein neues an — nicht beides.')
            )
        if not topic and not new_title:
            raise forms.ValidationError(
                _('Bitte wähle ein bestehendes Thema oder gib einen Titel für ein neues Thema ein.')
            )
        if new_title:
            exists = Topic.objects.filter(title__iexact=new_title).exists()
            if exists:
                self.add_error(
                    'new_topic_title',
                    _('Ein Thema mit diesem Titel existiert bereits — bitte wähle es oben aus der Liste.'),
                )
        cleaned['new_topic_title'] = new_title
        return cleaned

    def parsed_tags(self):
        raw = self.cleaned_data.get('tags') or ''
        return [t.strip() for t in raw.split(',') if t.strip()]
