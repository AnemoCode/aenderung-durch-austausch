from django.conf import settings


def staging(request):
    if not settings.STAGING:
        return {}
    from apps.blog.staging_data import SEED_USERS
    return {"staging_credentials": SEED_USERS}
