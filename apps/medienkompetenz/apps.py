from django.apps import AppConfig


class MedienkompetenzConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.medienkompetenz'
    verbose_name = 'Medienkompetenz'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_add_medienkompetenz_to_moderator_group, sender=self)


def _add_medienkompetenz_to_moderator_group(sender, **kwargs):
    import sys

    from django.contrib.auth.models import Group, Permission

    try:
        moderator, _ = Group.objects.get_or_create(name='Moderator')
        perms = Permission.objects.filter(content_type__app_label='medienkompetenz')
        if perms.exists():
            moderator.permissions.add(*perms)
    except Exception as exc:
        print(
            f"ERROR: Failed to add medienkompetenz permissions to Moderator group: {exc}",
            file=sys.stderr,
        )
