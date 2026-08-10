from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_site_settings(sender, **kwargs):
    """Make sure a SiteSettings row exists after migrations."""
    if sender.name == 'core':
        from .models import SiteSettings
        SiteSettings.get_solo()