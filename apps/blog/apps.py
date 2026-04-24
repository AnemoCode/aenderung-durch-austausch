from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blog'
    verbose_name = 'Blog'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_create_moderator_group, sender=self)


def _create_moderator_group(sender, **kwargs):
    import sys

    from django.contrib.auth.models import Group, Permission

    try:
        moderator, _ = Group.objects.get_or_create(name='Moderator')
        perms = Permission.objects.filter(content_type__app_label='blog')
        if not perms.exists():
            print(
                "WARNING: No blog permissions found for Moderator group — "
                "content types may not be synced yet.",
                file=sys.stderr,
            )
        moderator.permissions.set(perms)
    except Exception as exc:
        print(f"ERROR: Failed to create Moderator group: {exc}", file=sys.stderr)
