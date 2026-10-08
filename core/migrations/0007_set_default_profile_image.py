from django.db import migrations


def set_default_profile_image(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    obj, _ = SiteSettings.objects.get_or_create(pk=1)
    if not obj.profile_image:
        obj.profile_image = 'profile/profile.png'
        obj.save(update_fields=['profile_image'])


def unset_default_profile_image(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_erp_modules'),
    ]

    operations = [
        migrations.RunPython(set_default_profile_image, unset_default_profile_image),
    ]