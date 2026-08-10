from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_set_default_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='hero_video',
            field=models.FileField(blank=True, help_text='Short looping MP4/WebM shown behind the hero. Muted, autoplay. Best: under 5 MB, 720p or lower, ~10s loop.', null=True, upload_to='hero/'),
        ),
    ]