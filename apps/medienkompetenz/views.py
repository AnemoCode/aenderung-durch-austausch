"""Views for the Medienkompetenz pillar.

The article CRUD mirrors apps.definitions.  The interactive-block views are
type-aware: a single view family dispatches to the right form via the
``BLOCK_FORMS`` registry, so adding a new block type only requires a new form
and a new template — no view changes.

The image upload endpoint exists so the Quill editor can persist images to
``MEDIA_ROOT`` instead of embedding them as base64 strings.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from .forms import BLOCK_FORMS, ArticleForm
from .models import Article, InteractiveBlock, UploadedImage


ALLOWED_IMAGE_MIME_PREFIXES = ('image/jpeg', 'image/png', 'image/webp', 'image/gif')


class _StaffOrPermMixin(LoginRequiredMixin):
    """Login + (is_staff or named permission). Mirror of the definitions pattern."""

    login_url = reverse_lazy('accounts:login')
    permission_required: str | None = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            allowed = request.user.is_staff or (
                self.permission_required
                and request.user.has_perm(self.permission_required)
            )
            if not allowed:
                return redirect('medienkompetenz:index')
        return super().dispatch(request, *args, **kwargs)


class ArticleListView(ListView):
    template_name = 'medienkompetenz/article_list.html'
    context_object_name = 'articles'

    def _query(self) -> str:
        return (self.request.GET.get('q') or '').strip()

    def get_queryset(self):
        qs = (
            Article.objects.filter(is_published=True)
            .select_related('author')
            .prefetch_related('tags')
        )
        q = self._query()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(lead__icontains=q)
                | Q(body__icontains=q)
                | Q(tags__name__icontains=q)
            ).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'medienkompetenz'
        ctx['query'] = self._query()
        return ctx


class ArticleDetailView(DetailView):
    template_name = 'medienkompetenz/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        qs = (
            Article.objects.all()
            .select_related('author')
            .prefetch_related('tags', 'blocks')
        )
        user = self.request.user
        if user.is_authenticated and (
            user.is_staff or user.has_perm('medienkompetenz.change_article')
        ):
            return qs
        if user.is_authenticated:
            return qs.filter(Q(is_published=True) | Q(author=user))
        return qs.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'medienkompetenz'
        ctx['blocks'] = list(self.object.blocks.all())
        return ctx


class ArticleCreateView(_StaffOrPermMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'medienkompetenz/article_form.html'
    permission_required = 'medienkompetenz.add_article'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'medienkompetenz'
        ctx['is_edit'] = False
        return ctx

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        tags = form.parsed_tags()
        if tags:
            self.object.tags.add(*tags)
        messages.success(self.request, _('Beitrag veröffentlicht.'))
        return response


class ArticleUpdateView(_StaffOrPermMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'medienkompetenz/article_form.html'
    permission_required = 'medienkompetenz.change_article'

    def get_initial(self):
        initial = super().get_initial()
        initial['tags'] = ', '.join(self.object.tags.values_list('name', flat=True))
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'medienkompetenz'
        ctx['is_edit'] = True
        ctx['blocks'] = list(self.object.blocks.all())
        ctx['block_choices'] = InteractiveBlock.BlockType.choices
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tags.set(form.parsed_tags())
        messages.success(self.request, _('Beitrag aktualisiert.'))
        return response


# ─── Interactive block CRUD ─────────────────────────────────────────────────


def _resolve_block_form(block_type: str):
    """Return the form class for ``block_type`` or None if unknown."""
    return BLOCK_FORMS.get(block_type)


class _BlockEditMixin(_StaffOrPermMixin):
    permission_required = 'medienkompetenz.change_article'
    template_name = 'medienkompetenz/block_form.html'

    def get_article(self) -> Article:
        return get_object_or_404(Article, slug=self.kwargs['slug'])


class BlockCreateView(_BlockEditMixin, View):
    def get(self, request, slug, block_type):
        form_cls = _resolve_block_form(block_type)
        if form_cls is None:
            return redirect('medienkompetenz:edit', slug=slug)
        article = self.get_article()
        return self._render(request, article, block_type, form_cls())

    def post(self, request, slug, block_type):
        form_cls = _resolve_block_form(block_type)
        if form_cls is None:
            return redirect('medienkompetenz:edit', slug=slug)
        article = self.get_article()
        form = form_cls(request.POST)
        if form.is_valid():
            block = InteractiveBlock(
                article=article,
                order=article.blocks.count(),
            )
            form.apply_to(block)
            block.save()
            messages.success(request, _('Abschnitt hinzugefügt.'))
            return redirect('medienkompetenz:edit', slug=slug)
        return self._render(request, article, block_type, form)

    @staticmethod
    def _render(request, article, block_type, form):
        return render(request, 'medienkompetenz/block_form.html', {
            'active_nav': 'medienkompetenz',
            'article': article,
            'form': form,
            'block_type': block_type,
            'block_type_label': dict(InteractiveBlock.BlockType.choices).get(block_type, block_type),
            'is_edit': False,
        })


class BlockUpdateView(_BlockEditMixin, View):
    def get(self, request, slug, pk):
        article = self.get_article()
        block = get_object_or_404(InteractiveBlock, pk=pk, article=article)
        form_cls = _resolve_block_form(block.block_type)
        if form_cls is None:
            return redirect('medienkompetenz:edit', slug=slug)
        form = form_cls(initial=form_cls.initial_from(block))
        return self._render(request, article, block, form)

    def post(self, request, slug, pk):
        article = self.get_article()
        block = get_object_or_404(InteractiveBlock, pk=pk, article=article)
        form_cls = _resolve_block_form(block.block_type)
        if form_cls is None:
            return redirect('medienkompetenz:edit', slug=slug)
        form = form_cls(request.POST)
        if form.is_valid():
            form.apply_to(block)
            block.save()
            messages.success(request, _('Abschnitt aktualisiert.'))
            return redirect('medienkompetenz:edit', slug=slug)
        return self._render(request, article, block, form)

    @staticmethod
    def _render(request, article, block, form):
        return render(request, 'medienkompetenz/block_form.html', {
            'active_nav': 'medienkompetenz',
            'article': article,
            'block': block,
            'form': form,
            'block_type': block.block_type,
            'block_type_label': block.get_block_type_display(),
            'is_edit': True,
        })


class BlockDeleteView(_BlockEditMixin, View):
    def post(self, request, slug, pk):
        article = self.get_article()
        block = get_object_or_404(InteractiveBlock, pk=pk, article=article)
        block.delete()
        messages.success(request, _('Abschnitt entfernt.'))
        return redirect('medienkompetenz:edit', slug=slug)


# ─── Inline image upload (for Quill editor) ──────────────────────────────────


@require_POST
def image_upload(request):
    """Accept a single image file, store it under MEDIA_ROOT, return its URL.

    Used by the Quill editor's image handler so embedded images live on disk
    (configurable via MEDIA_ROOT) instead of being inlined as base64.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth required'}, status=401)
    if not (request.user.is_staff or request.user.has_perm('medienkompetenz.add_article')):
        return JsonResponse({'error': 'forbidden'}, status=403)

    upload = request.FILES.get('image')
    if upload is None:
        return JsonResponse({'error': _('Keine Datei empfangen.')}, status=400)

    max_bytes = getattr(settings, 'MEDIA_UPLOAD_MAX_BYTES', 8 * 1024 * 1024)
    if upload.size > max_bytes:
        return JsonResponse(
            {'error': _('Datei ist größer als das erlaubte Maximum.')},
            status=400,
        )

    content_type = (upload.content_type or '').lower()
    if not content_type.startswith('image/') or content_type not in ALLOWED_IMAGE_MIME_PREFIXES:
        return JsonResponse({'error': _('Dateityp nicht erlaubt.')}, status=400)

    # Compose a safe filename: random uuid + lower-cased extension from the
    # upload's reported name.  Avoids relying on user-supplied paths.
    suffix = Path(upload.name).suffix.lower() or '.bin'
    safe_name = f'medienkompetenz/blocks/{uuid.uuid4().hex}{suffix}'
    saved_path = default_storage.save(safe_name, upload)

    record = UploadedImage.objects.create(
        file=saved_path,
        uploaded_by=request.user,
    )
    return JsonResponse({
        'url': record.file.url,
        'name': Path(saved_path).name,
        'id': record.pk,
    })
