from django.contrib import admin

from .models import Definition


@admin.register(Definition)
class DefinitionAdmin(admin.ModelAdmin):
    list_display = ['term', 'slug', 'author', 'is_published', 'updated_at']
    list_filter = ['is_published', 'author', 'tags']
    search_fields = ['term', 'slug', 'simple_explanation', 'formal_explanation', 'tags__name']
    prepopulated_fields = {'slug': ('term',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['term']
