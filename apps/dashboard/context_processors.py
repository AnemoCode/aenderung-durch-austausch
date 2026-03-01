from .models import Project


def onboarding(request):
    """Inject the first incomplete onboarding step (1 or 2) into every template context."""
    if not request.user.is_authenticated:
        return {}

    has_token = bool(request.user.overleaf_token)
    if not has_token:
        return {'onboarding_step': 1}

    has_project = Project.objects.filter(owner=request.user).exists()
    if not has_project:
        return {'onboarding_step': 2}

    return {}
