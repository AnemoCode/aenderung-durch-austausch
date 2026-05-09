from django.contrib import admin
from django.utils.html import format_html

from .models import Topic, TopicPart


class TopicPartInline(admin.StackedInline):
    model = TopicPart
    extra = 0
    fields = ['title', 'body', 'order']
    ordering = ['order']

    def get_readonly_fields(self, request, obj=None):
        return ['body_preview'] if obj else []

    def body_preview(self, obj):
        return format_html('<div style="max-height:150px;overflow:auto;">{}</div>', obj.body)
    body_preview.short_description = 'Vorschau'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    ordering = ['title']
    inlines = [TopicPartInline]


@admin.register(TopicPart)
class TopicPartAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'order', 'updated_at']
    list_filter = ['topic']
    search_fields = ['title', 'body']
    ordering = ['topic', 'order']
    readonly_fields = ['body_preview']

    def body_preview(self, obj):
        return format_html('<div style="max-height:200px;overflow:auto;border:1px solid #eee;padding:8px;">{}</div>', obj.body)
    body_preview.short_description = 'Vorschau (gerendert)'
