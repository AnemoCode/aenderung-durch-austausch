import bleach
from bleach.css_sanitizer import CSSSanitizer
from django import forms
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from .models import Definition

_ALLOWED_TAGS = [
    'p', 'br',
    'h2', 'h3', 'h4',
    'strong', 'em', 'u', 's',
    'ul', 'ol', 'li',
    'blockquote', 'pre', 'code',
    'a', 'span',
    'img',
    'iframe',
    'figure', 'figcaption',
]
_ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'pre': ['class', 'spellcheck'],
    'p': ['class'],
    'li': ['class'],
    'ol': ['class', 'start'],
    'ul': ['class'],
    'span': ['class'],
    'img': ['src', 'alt', 'width', 'height', 'class', 'style'],
    'iframe': ['src', 'class', 'width', 'height', 'frameborder', 'allowfullscreen'],
    'figure': ['class'],
    'figcaption': ['class'],
}

# Allowlist for the img `style` attribute so bleach actually sanitizes inline
# CSS (sizing) instead of dropping it and emitting a NoCssSanitizerWarning.
_CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=[
        'width', 'height',
        'float', 'margin', 'margin-left', 'margin-right',
    ]
)


class DefinitionForm(forms.ModelForm):
    """Create/edit form for a Definition, with rich text explanations and free-text tags."""

    tags = forms.CharField(
        required=False,
        label=_('Tags'),
        help_text=_('Kommagetrennt, z. B. "Rassismus, Geschichte"'),
    )

    class Meta:
        model = Definition
        fields = ['term', 'simple_explanation', 'formal_explanation', 'references']
        labels = {
            'term': _('Begriff'),
            'simple_explanation': _('Erklärung in einfacher Sprache'),
            'formal_explanation': _('Formale Definition'),
            'references': _('Quellenangaben & Verweise'),
        }
        widgets = {
            'simple_explanation': forms.Textarea(attrs={'rows': 10}),
            'formal_explanation': forms.Textarea(attrs={'rows': 10}),
            'references': forms.Textarea(attrs={'rows': 5}),
        }

    def _sanitize(self, raw: str) -> str:
        return bleach.clean(
            raw or '',
            tags=_ALLOWED_TAGS,
            attributes=_ALLOWED_ATTRS,
            css_sanitizer=_CSS_SANITIZER,
            strip=True,
        )

    def clean_simple_explanation(self):
        sanitized = self._sanitize(self.cleaned_data.get('simple_explanation', ''))
        if not strip_tags(sanitized).strip():
            raise forms.ValidationError(_('Bitte fülle die einfache Erklärung aus.'))
        return sanitized

    def clean_formal_explanation(self):
        sanitized = self._sanitize(self.cleaned_data.get('formal_explanation', ''))
        if not strip_tags(sanitized).strip():
            raise forms.ValidationError(_('Bitte fülle die formale Definition aus.'))
        return sanitized

    def clean_references(self):
        return self._sanitize(self.cleaned_data.get('references', ''))

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
