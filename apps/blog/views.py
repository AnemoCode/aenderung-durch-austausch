from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView

from .forms import CommentForm, PostForm
from .models import Like, Post


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return (
            Post.objects.filter(is_published=True)
            .select_related('author')
            .prefetch_related('likes', 'comments')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'index'
        ctx['user_liked'] = set(
            Like.objects.filter(user=self.request.user).values_list('post_id', flat=True)
        )
        return ctx


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.objects.select_related('author').prefetch_related('comments__author', 'likes'),
            pk=self.kwargs['pk'],
            is_published=True,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'index'
        ctx['comment_form'] = CommentForm()
        ctx['user_liked'] = Like.objects.filter(post=self.object, user=self.request.user).exists()
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, _('Kommentar hinzugefügt.'))
            return redirect(reverse('blog:post_detail', kwargs={'pk': self.object.pk}))
        ctx = self.get_context_data()
        ctx['comment_form'] = form
        return self.render_to_response(ctx)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, _('Beitrag veröffentlicht.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_nav'] = 'index'
        return ctx


@login_required
def like_toggle(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    post = get_object_or_404(Post, pk=pk, is_published=True)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return JsonResponse({
        'liked': created,
        'count': post.likes.count(),
    })
