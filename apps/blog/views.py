from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, RedirectView, TemplateView
from taggit.models import Tag

from .forms import CommentForm
from .models import Like, Topic, TopicPart


class TopicListView(ListView):
    model = Topic
    template_name = 'blog/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return (
            Topic.objects.filter(is_published=True)
            .select_related('author')
            .prefetch_related('tags', 'parts', 'likes', 'comments')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'index'
        return ctx


class TopicDetailView(DetailView):
    model = Topic
    template_name = 'blog/topic_detail.html'
    context_object_name = 'topic'

    def get_queryset(self):
        return (
            Topic.objects.filter(is_published=True)
            .select_related('author')
            .prefetch_related('tags', 'parts__tags', 'comments__author', 'likes')
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
        topic = get_object_or_404(Topic, legacy_post_id=kwargs['pk'])
        return topic.get_absolute_url()


class TagDetailView(TemplateView):
    template_name = 'blog/tag_detail.html'

    def get_context_data(self, **kwargs):
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
        ctx['active_nav'] = 'index'
        return ctx


@login_required
def topic_like_toggle(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    topic = get_object_or_404(Topic, slug=slug, is_published=True)
    like, created = Like.objects.get_or_create(topic=topic, user=request.user)
    if not created:
        like.delete()
    return JsonResponse({
        'liked': created,
        'count': topic.likes.count(),
    })
