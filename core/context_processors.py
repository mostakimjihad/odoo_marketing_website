from .models import SiteSettings, Service, ERPModule


def site_settings(request):
    """Make the SiteSettings singleton available to all templates."""
    try:
        settings_obj = SiteSettings.objects.first()
    except Exception:
        # DB may not be ready (e.g. during initial migrate).
        settings_obj = None
    return {'site_settings': settings_obj}


def mega_menu(request):
    """Top services + featured modules for the navbar mega menu panels.

    Wrapped in try/except so a transient DB issue during `migrate` or
    first-boot never crashes template rendering.
    """
    try:
        top_services = list(
            Service.objects.filter(is_active=True)
            .order_by('order', 'title')[:6]
        )
        featured_modules = list(
            ERPModule.objects.filter(is_published=True, is_featured=True)
            .order_by('order', 'title')[:4]
        )
    except Exception:
        top_services = []
        featured_modules = []
    return {
        'mega_top_services': top_services,
        'mega_featured_modules': featured_modules,
    }