"""Forms for Medienkompetenz articles and their interactive blocks.

Each interactive block type has a dedicated form so the admin UI stays simple
and the JSON shape in ``InteractiveBlock.data`` is enforced at the form layer
rather than buried in template logic.  Adding a new block type means:

1. add a value to ``InteractiveBlock.BlockType``
2. add a form subclass below that overrides ``build_data`` / ``initial_from``
3. register it in ``BLOCK_FORMS``
4. add a renderer template under ``medienkompetenz/blocks/``
"""
from __future__ import annotations

from typing import Any

import bleach
from bleach.css_sanitizer import CSSSanitizer
from django import forms
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from .models import Article, InteractiveBlock


# Rich-text allowlist for body/instructions/references fields.
# Mirrors apps.definitions.forms but also permits img + iframe (videos), since
# Medienkompetenz articles are explicitly multimedia-heavy.
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
    'iframe': [
        'src', 'class', 'width', 'height',
        'frameborder', 'allowfullscreen', 'allow',
        'title',
    ],
    'figure': ['class'],
    'figcaption': ['class'],
}


# Sanitize the `style` attribute rather than dropping it: the Quill image-resize
# module stores the dragged dimensions as inline `width`/`height`, so an
# allowlisted CSS sanitizer is what lets editors resize images and have that
# size survive save. Anything outside this property list is stripped.
_CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=[
        'width', 'height',
        'float', 'margin', 'margin-left', 'margin-right',
    ]
)


def _sanitize(raw: str) -> str:
    return bleach.clean(
        raw or '',
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        css_sanitizer=_CSS_SANITIZER,
        strip=True,
    )


class ArticleForm(forms.ModelForm):
    """Create/edit form for a Medienkompetenz article.

    Tags are free-form comma-separated text (consistent with other apps).
    Rich-text fields are sanitized via bleach to prevent stored XSS.
    """

    tags = forms.CharField(
        required=False,
        label=_('Tags'),
        help_text=_('Kommagetrennt, z. B. "ki-bilder, deepfake, framing"'),
    )

    class Meta:
        model = Article
        fields = ['title', 'lead', 'hero_image', 'body', 'references', 'is_published']
        labels = {
            'title': _('Titel'),
            'lead': _('Einleitung'),
            'hero_image': _('Titelbild'),
            'body': _('Inhalt'),
            'references': _('Quellenangaben & Verweise'),
            'is_published': _('Veröffentlicht'),
        }
        widgets = {
            'lead': forms.Textarea(attrs={'rows': 2}),
            'body': forms.Textarea(attrs={'rows': 12}),
            'references': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_body(self):
        sanitized = _sanitize(self.cleaned_data.get('body', ''))
        if not strip_tags(sanitized).strip():
            raise forms.ValidationError(_('Bitte gib einen Inhalt ein.'))
        return sanitized

    def clean_references(self):
        return _sanitize(self.cleaned_data.get('references', ''))

    def parsed_tags(self) -> list[str]:
        raw = self.cleaned_data.get('tags') or ''
        return [t.strip() for t in raw.split(',') if t.strip()]


# ─── Interactive block forms ────────────────────────────────────────────────
# Each form owns its own JSON schema for InteractiveBlock.data and converts
# between flat form fields ↔ structured data.  The shared base handles the
# metadata fields (title, instructions, order) so subclasses only define the
# type-specific shape.


class _BaseBlockForm(forms.Form):
    """Shared fields for every interactive block form."""

    title = forms.CharField(
        max_length=200,
        required=False,
        label=_('Titel'),
        help_text=_('Optional. Wird über dem interaktiven Abschnitt angezeigt.'),
    )
    instructions = forms.CharField(
        required=False,
        label=_('Anleitung'),
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text=_('Kurze Einleitung zum Abschnitt.'),
    )

    #: Subclasses set this to the matching ``InteractiveBlock.BlockType`` value.
    block_type: str = ''

    def clean_instructions(self):
        return _sanitize(self.cleaned_data.get('instructions', ''))

    def build_data(self) -> dict[str, Any]:
        """Return the JSON payload to store in InteractiveBlock.data.

        Subclasses override this; defaults to an empty dict.
        """
        return {}

    @classmethod
    def initial_from(cls, block: InteractiveBlock) -> dict[str, Any]:
        """Map an existing block back to the form's initial data."""
        return {
            'title': block.title,
            'instructions': block.instructions,
        }

    def apply_to(self, block: InteractiveBlock) -> None:
        """Populate fields on ``block`` from this form's cleaned data."""
        block.block_type = self.block_type
        block.title = self.cleaned_data.get('title', '')
        block.instructions = self.cleaned_data.get('instructions', '')
        block.data = self.build_data()


class AiImageQuizForm(_BaseBlockForm):
    """Quiz: reader sees N images, decides which are AI-generated.

    ``items_raw`` is one item per line; each line is
    ``image_url | ai|real | optional explanation``.
    """

    block_type = InteractiveBlock.BlockType.AI_IMAGE_QUIZ

    items_raw = forms.CharField(
        required=True,
        label=_('Bilder'),
        widget=forms.Textarea(attrs={'rows': 8}),
        help_text=_(
            'Eine Zeile pro Bild im Format: BILD-URL | ki|echt | optionale Erklärung. '
            'Bilder zuerst über das Upload-Feld hochladen und die URL einfügen.'
        ),
    )

    def clean_items_raw(self):
        raw = self.cleaned_data.get('items_raw', '').strip()
        items = []
        for lineno, line in enumerate(raw.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 2:
                raise forms.ValidationError(
                    _('Zeile %(n)d: Bitte URL und Antwort (ki/echt) angeben.') % {'n': lineno}
                )
            image, answer, *rest = parts
            answer = answer.lower()
            if answer not in ('ki', 'echt'):
                raise forms.ValidationError(
                    _('Zeile %(n)d: Antwort muss "ki" oder "echt" sein.') % {'n': lineno}
                )
            explanation = ' | '.join(rest).strip() if rest else ''
            items.append({
                'image': image,
                'is_ai': answer == 'ki',
                'explanation': _sanitize(explanation),
            })
        if not items:
            raise forms.ValidationError(_('Bitte mindestens ein Bild angeben.'))
        return items

    def build_data(self) -> dict[str, Any]:
        return {'items': self.cleaned_data['items_raw']}

    @classmethod
    def initial_from(cls, block: InteractiveBlock) -> dict[str, Any]:
        initial = super().initial_from(block)
        lines = []
        for item in (block.data or {}).get('items', []):
            answer = 'ki' if item.get('is_ai') else 'echt'
            explanation = item.get('explanation') or ''
            parts = [item.get('image', ''), answer]
            if explanation:
                parts.append(strip_tags(explanation))
            lines.append(' | '.join(parts))
        initial['items_raw'] = '\n'.join(lines)
        return initial


class FramingExerciseForm(_BaseBlockForm):
    """Framing exercise: reader picks the option that names the framing.

    ``scenarios_raw`` uses ``---`` as a scenario delimiter; within a scenario,
    the first non-empty line is the prompt, then lines are options prefixed
    with ``*`` for the correct one. Optional ``> explanation`` lines explain
    each option (most recent option line wins).
    """

    block_type = InteractiveBlock.BlockType.FRAMING_EXERCISE

    scenarios_raw = forms.CharField(
        required=True,
        label=_('Szenarien'),
        widget=forms.Textarea(attrs={'rows': 12}),
        help_text=_(
            'Szenarien mit "---" trennen. Erste Zeile = Aussage; danach Optionen '
            '(eine pro Zeile). Markiere die korrekte Option mit "*" am Zeilenanfang. '
            'Optional folgt eine Erklärung mit "> ..." nach der Option.'
        ),
    )

    def clean_scenarios_raw(self):
        raw = self.cleaned_data.get('scenarios_raw', '').strip()
        scenarios: list[dict[str, Any]] = []
        blocks = [b.strip() for b in raw.split('---') if b.strip()]
        for idx, block in enumerate(blocks, start=1):
            lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
            if not lines:
                continue
            prompt = lines[0]
            options: list[dict[str, Any]] = []
            for line in lines[1:]:
                if line.startswith('>') and options:
                    options[-1]['explanation'] = _sanitize(line[1:].strip())
                    continue
                is_correct = line.startswith('*')
                label = line[1:].strip() if is_correct else line.strip()
                options.append({
                    'label': label,
                    'is_correct': is_correct,
                    'explanation': '',
                })
            if len(options) < 2:
                raise forms.ValidationError(
                    _('Szenario %(n)d: Mindestens zwei Optionen pro Szenario.') % {'n': idx}
                )
            if not any(o['is_correct'] for o in options):
                raise forms.ValidationError(
                    _('Szenario %(n)d: Eine Option muss mit "*" als korrekt markiert sein.') % {'n': idx}
                )
            scenarios.append({'prompt': prompt, 'options': options})
        if not scenarios:
            raise forms.ValidationError(_('Bitte mindestens ein Szenario angeben.'))
        return scenarios

    def build_data(self) -> dict[str, Any]:
        return {'scenarios': self.cleaned_data['scenarios_raw']}

    @classmethod
    def initial_from(cls, block: InteractiveBlock) -> dict[str, Any]:
        initial = super().initial_from(block)
        out: list[str] = []
        for scenario in (block.data or {}).get('scenarios', []):
            out.append(scenario.get('prompt', ''))
            for opt in scenario.get('options', []):
                prefix = '*' if opt.get('is_correct') else ''
                out.append(f"{prefix}{opt.get('label', '')}")
                exp = strip_tags(opt.get('explanation') or '').strip()
                if exp:
                    out.append(f"> {exp}")
            out.append('---')
        if out and out[-1] == '---':
            out.pop()
        initial['scenarios_raw'] = '\n'.join(out)
        return initial


class TextCalloutForm(_BaseBlockForm):
    """A formatted callout / aside — handy for "Pro tip" or warning boxes."""

    block_type = InteractiveBlock.BlockType.TEXT_CALLOUT

    tone = forms.ChoiceField(
        required=True,
        label=_('Ton'),
        choices=[
            ('info', _('Hinweis')),
            ('warning', _('Achtung')),
            ('tip', _('Tipp')),
        ],
        initial='info',
    )
    body = forms.CharField(
        required=True,
        label=_('Text'),
        widget=forms.Textarea(attrs={'rows': 6}),
    )

    def clean_body(self):
        sanitized = _sanitize(self.cleaned_data.get('body', ''))
        if not strip_tags(sanitized).strip():
            raise forms.ValidationError(_('Bitte einen Text eingeben.'))
        return sanitized

    def build_data(self) -> dict[str, Any]:
        return {
            'tone': self.cleaned_data['tone'],
            'body': self.cleaned_data['body'],
        }

    @classmethod
    def initial_from(cls, block: InteractiveBlock) -> dict[str, Any]:
        initial = super().initial_from(block)
        initial['tone'] = (block.data or {}).get('tone', 'info')
        initial['body'] = (block.data or {}).get('body', '')
        return initial


#: Registry: block_type → form class. Keep all forms reachable by string key
#: so the URL routing can resolve them generically.
BLOCK_FORMS: dict[str, type[_BaseBlockForm]] = {
    InteractiveBlock.BlockType.AI_IMAGE_QUIZ: AiImageQuizForm,
    InteractiveBlock.BlockType.FRAMING_EXERCISE: FramingExerciseForm,
    InteractiveBlock.BlockType.TEXT_CALLOUT: TextCalloutForm,
}
