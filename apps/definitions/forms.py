from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Definition


class DefinitionForm(forms.ModelForm):
    """Create/edit form for a Definition, with a free-text tags field."""

    tags = forms.CharField(
        required=False,
        label=_('Tags'),
        help_text=_('Kommagetrennt, z. B. "rassismus, geschichte"'),
    )

    class Meta:
        model = Definition
        fields = ['term', 'simple_explanation', 'formal_explanation']
        labels = {
            'term': _('Begriff'),
            'simple_explanation': _('Erklärung in einfacher Sprache'),
            'formal_explanation': _('Formale Definition'),
        }
        widgets = {
            'simple_explanation': forms.Textarea(attrs={'rows': 10}),
            'formal_explanation': forms.Textarea(attrs={'rows': 10}),
        }

    def clean_term(self):
        term = (self.cleaned_data.get('term') or '').strip()
        qs = Definition.objects.filter(term__iexact=term)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                _('Es existiert bereits eine Definition für diesen Begriff.')
            )
        return term

    def parsed_tags(self) -> list[str]:
        raw = self.cleaned_data.get('tags') or ''
        return [t.strip() for t in raw.split(',') if t.strip()]
