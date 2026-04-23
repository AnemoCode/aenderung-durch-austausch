from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blog'
    verbose_name = 'Blog'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_create_moderator_group, sender=self)


def _create_moderator_group(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission

    try:
        moderator, _ = Group.objects.get_or_create(name='Moderator')
        perms = Permission.objects.filter(
            codename__in=['add_topicpart', 'add_comment', 'delete_comment'],
            content_type__app_label='blog',
        )
        moderator.permissions.add(*perms)
    except Exception:
        pass
