import string

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import DefinitionForm
from .models import Definition


LETTERS = list(string.ascii_uppercase) + ['#']


class _StaffRequiredMixin(LoginRequiredMixin):
    """Require login + is_staff. Non-staff are bounced to the list view."""

    login_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            return redirect('definitions:index')
        return super().dispatch(request, *args, **kwargs)


class DefinitionListView(ListView):
    """Dictionary-style list of definitions with letter filter + search."""

    template_name = 'definitions/definition_list.html'
    context_object_name = 'definitions'

    def _letter(self) -> str | None:
        raw = (self.request.GET.get('letter') or '').strip().upper()
        if raw in LETTERS:
            return raw
        return None

    def _query(self) -> str:
        return (self.request.GET.get('q') or '').strip()

    def get_queryset(self):
        qs = Definition.objects.filter(is_published=True).prefetch_related('tags')
        q = self._query()
        if q:
            qs = qs.filter(
                Q(term__icontains=q)
                | Q(simple_explanation__icontains=q)
                | Q(formal_explanation__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        all_defs = list(ctx['definitions'])
        letter = self._letter()

        active_letters = {d.initial_letter for d in all_defs}

        if letter:
            visible = [d for d in all_defs if d.initial_letter == letter]
        else:
            visible = all_defs

        # Group by initial letter, preserving alphabetical order via LETTERS.
        grouped: dict[str, list[Definition]] = {}
        for d in visible:
            grouped.setdefault(d.initial_letter, []).append(d)
        ordered_groups = [(L, grouped[L]) for L in LETTERS if L in grouped]

        ctx.update({
            'active_nav': 'definitionen',
            'letters': LETTERS,
            'active_letter': letter,
            'active_letters': active_letters,
            'query': self._query(),
            'grouped': ordered_groups,
            'total_count': len(all_defs),
            'visible_count': len(visible),
        })
        return ctx


class DefinitionDetailView(DetailView):
    template_name = 'definitions/definition_detail.html'
    context_object_name = 'definition'

    def get_queryset(self):
        return Definition.objects.filter(is_published=True).prefetch_related('tags')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'definitionen'
        return ctx


class DefinitionCreateView(_StaffRequiredMixin, CreateView):
    model = Definition
    form_class = DefinitionForm
    template_name = 'definitions/definition_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'definitionen'
        ctx['is_edit'] = False
        return ctx

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        tags = form.parsed_tags()
        if tags:
            self.object.tags.add(*tags)
        messages.success(self.request, _('Definition veröffentlicht.'))
        return response


class DefinitionUpdateView(_StaffRequiredMixin, UpdateView):
    model = Definition
    form_class = DefinitionForm
    template_name = 'definitions/definition_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['tags'] = ', '.join(self.object.tags.values_list('name', flat=True))
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'definitionen'
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tags.set(form.parsed_tags())
        messages.success(self.request, _('Definition aktualisiert.'))
        return response
