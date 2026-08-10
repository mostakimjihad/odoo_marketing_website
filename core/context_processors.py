from .models import SiteSettings


def site_settings(request):
    """Make the SiteSettings singleton available to all templates."""
    try:
        settings_obj = SiteSettings.objects.first()
    except Exception:
        # DB may not be ready (e.g. during initial migrate).
        settings_obj = None
    return {'site_settings': settings_obj}