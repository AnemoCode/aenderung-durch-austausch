from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, RedirectView, TemplateView
from taggit.models import Tag

from .forms import CommentForm, TopicPartCreateForm
from .models import Like, Topic, TopicPart


GROUP_CHOICES = ('topic', 'author', 'none')
SORT_CHOICES = ('date_desc', 'date_asc', 'likes_desc')


class TopicListView(ListView):
    """Part-centric blog index with grouping (topic/author/none) and sorting."""

    template_name = 'blog/topic_list.html'
    context_object_name = 'parts'

    def _group(self):
        value = self.request.GET.get('group', 'topic')
        return value if value in GROUP_CHOICES else 'topic'

    def _sort(self):
        value = self.request.GET.get('sort', 'date_desc')
        return value if value in SORT_CHOICES else 'date_desc'

    def get_queryset(self):
        qs = (
            TopicPart.objects.filter(topic__is_published=True)
            .select_related('topic', 'topic__author', 'author')
            .prefetch_related('tags', 'topic__tags')
            .annotate(topic_likes=Count('topic__likes', distinct=True))
        )
        sort = self._sort()
        if sort == 'date_asc':
            return qs.order_by('created_at')
        if sort == 'likes_desc':
            return qs.order_by('-topic_likes', '-created_at')
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        parts = list(ctx['parts'])
        group = self._group()
        ctx['active_nav'] = 'index'
        ctx['group'] = group
        ctx['sort'] = self._sort()
        ctx['groups'] = self._build_groups(parts, group)
        ctx['total_parts'] = len(parts)
        ctx['show_topic_on_card'] = group != 'topic'
        ctx['show_author_on_card'] = group != 'author'
        return ctx

    @staticmethod
    def _build_groups(parts, group):
        """Return a list of (key, label, meta, parts) tuples preserving sort order."""
        if group == 'none':
            return [(None, None, None, parts)] if parts else []

        buckets = {}
        order = []
        for part in parts:
            if group == 'topic':
                key = part.topic.pk
                label = part.topic.title
                meta = {
                    'type': 'topic',
                    'topic': part.topic,
                }
            else:  # author
                key = part.author.pk
                label = part.author.name
                meta = {
                    'type': 'author',
                    'author': part.author,
                }
            if key not in buckets:
                buckets[key] = (key, label, meta, [])
                order.append(key)
            buckets[key][3].append(part)
        return [buckets[k] for k in order]


class TopicDetailView(DetailView):
    model = Topic
    template_name = 'blog/topic_detail.html'
    context_object_name = 'topic'

    def get_queryset(self):
        return (
            Topic.objects.filter(is_published=True)
            .select_related('author')
            .prefetch_related('tags', 'parts__tags', 'comments__author')
            .annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'index'
        ctx['parts'] = self.object.parts.all()
        ctx['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            ctx['user_liked'] = Like.objects.filter(
                topic=self.object, user=self.request.user
            ).exists()
        else:
            ctx['user_liked'] = False
        return ctx

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.topic = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, _('Kommentar hinzugefügt.'))
            return redirect(self.object.get_absolute_url())
        ctx = self.get_context_data()
        ctx['comment_form'] = form
        return self.render_to_response(ctx)


class PostDetailRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        topic = get_object_or_404(
            Topic, legacy_post_id=kwargs['pk'], is_published=True
        )
        return topic.get_absolute_url()


class TagDetailView(TemplateView):
    template_name = 'blog/tag_detail.html'

    def get_context_data(self, **kwargs):
        # Inline import: apps.definitions imports nothing from blog, but
        # keeping the dependency local to this method documents that blog
        # does not require definitions to load — the two apps remain
        # independent at import time.
        from apps.definitions.models import Definition

        ctx = super().get_context_data(**kwargs)
        slug = kwargs['slug']
        tag = get_object_or_404(Tag, slug=slug)
        ctx['tag'] = tag
        ctx['topics'] = (
            Topic.objects.filter(tags__slug=slug, is_published=True)
            .select_related('author')
            .prefetch_related('tags')
            .distinct()
        )
        ctx['parts'] = (
            TopicPart.objects.filter(tags__slug=slug, topic__is_published=True)
            .select_related('topic')
            .prefetch_related('tags')
            .distinct()
        )
        ctx['definitions'] = (
            Definition.objects.filter(tags__slug=slug, is_published=True)
            .prefetch_related('tags')
            .distinct()
        )
        ctx['active_nav'] = 'index'
        return ctx


class TopicPartCreateView(LoginRequiredMixin, FormView):
    template_name = 'blog/post_form.html'
    form_class = TopicPartCreateForm
    login_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'index'
        return ctx

    def form_valid(self, form):
        user = self.request.user
        with transaction.atomic():
            topic = form.cleaned_data.get('topic')
            if topic is None:
                topic = Topic.objects.create(
                    author=user,
                    title=form.cleaned_data['new_topic_title'],
                    is_published=True,
                )
            part = TopicPart.objects.create(
                topic=topic,
                author=user,
                heading=form.cleaned_data['heading'],
                body=form.cleaned_data['body'],
                order=topic.parts.count(),
            )
            tags = form.parsed_tags()
            if tags:
                part.tags.add(*tags)
        messages.success(self.request, _('Beitrag veröffentlicht.'))
        self._created_topic = topic
        return super().form_valid(form)

    def get_success_url(self):
        return self._created_topic.get_absolute_url()


def topic_like_toggle(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    topic = get_object_or_404(Topic, slug=slug, is_published=True)
    like, created = Like.objects.get_or_create(topic=topic, user=request.user)
    if not created:
        like.delete()
    return JsonResponse({
        'liked': created,
        'count': topic.likes.count(),
    })
