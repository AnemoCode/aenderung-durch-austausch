from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import TopicPartForm
from .models import Topic, TopicPart


class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'topics/topic_list.html'
    context_object_name = 'topics'


class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic
    template_name = 'topics/topic_detail.html'
    context_object_name = 'topic'

    def get_queryset(self):
        return Topic.objects.prefetch_related('parts')


class TopicPartCreateView(LoginRequiredMixin, CreateView):
    model = TopicPart
    form_class = TopicPartForm
    template_name = 'topics/topicpart_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('topics:topic_list')
        self.topic = get_object_or_404(Topic, pk=kwargs['topic_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.topic = self.topic
        messages.success(self.request, _('Themanteil gespeichert.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('topics:topic_detail', kwargs={'pk': self.topic.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['topic'] = self.topic
        ctx['is_edit'] = False
        return ctx


class TopicPartUpdateView(LoginRequiredMixin, UpdateView):
    model = TopicPart
    form_class = TopicPartForm
    template_name = 'topics/topicpart_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('topics:topic_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _('Themanteil aktualisiert.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('topics:topic_detail', kwargs={'pk': self.object.topic.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['topic'] = self.object.topic
        ctx['is_edit'] = True
        return ctx
