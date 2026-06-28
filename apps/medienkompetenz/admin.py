from django.contrib import admin

from .models import Article, InteractiveBlock, UploadedImage


class InteractiveBlockInline(admin.StackedInline):
    model = InteractiveBlock
    extra = 0
    fields = ['order', 'block_type', 'title', 'instructions', 'data']
    ordering = ['order']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'is_published', 'updated_at']
    list_filter = ['is_published', 'author', 'tags']
    search_fields = ['title', 'slug', 'lead', 'body', 'tags__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    inlines = [InteractiveBlockInline]


@admin.register(InteractiveBlock)
class InteractiveBlockAdmin(admin.ModelAdmin):
    list_display = ['article', 'order', 'block_type', 'title', 'updated_at']
    list_filter = ['block_type', 'article']
    search_fields = ['title', 'instructions', 'article__title']
    ordering = ['article', 'order']


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ['file', 'uploaded_by', 'created_at']
    list_filter = ['uploaded_by']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
