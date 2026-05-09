from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TopicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.topics'
    verbose_name = _('Themen')
