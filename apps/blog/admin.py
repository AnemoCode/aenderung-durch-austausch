from django.contrib import admin

from .models import Comment, Like, Topic, TopicPart


class TopicPartInline(admin.StackedInline):
    model = TopicPart
    extra = 1
    fields = ['order', 'author', 'heading', 'body', 'tags']
    ordering = ['order']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'is_published', 'created_at']
    list_filter = ['is_published', 'author', 'tags']
    search_fields = ['title', 'slug', 'tags__name']
    ordering = ['-created_at']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TopicPartInline]


@admin.register(TopicPart)
class TopicPartAdmin(admin.ModelAdmin):
    list_display = ['topic', 'order', 'heading', 'author', 'created_at']
    list_filter = ['topic', 'author', 'tags']
    search_fields = ['heading', 'body', 'topic__title', 'author__name', 'tags__name']
    ordering = ['topic', 'order']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'topic', 'created_at']
    list_filter = ['topic']
    ordering = ['-created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'created_at']
    list_filter = ['topic']
    ordering = ['-created_at']
