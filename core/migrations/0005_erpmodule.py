from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_seed_site_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ERPModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, help_text="Module name, e.g. 'Point of Sale', 'Accounting', 'Manufacturing'.")),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('short_tag', models.CharField(default='', help_text="Short code shown on the tile, e.g. 'POS', 'ACC', 'MRP'.", max_length=20)),
                ('category', models.CharField(choices=[
                    ('operations', 'Operations'),
                    ('sales', 'Sales & Commerce'),
                    ('finance', 'Finance & Accounting'),
                    ('people', 'People & HR'),
                    ('web', 'Web & Marketing'),
                    ('productivity', 'Productivity'),
                ], default='operations', max_length=20)),
                ('tagline', models.CharField(blank=True, help_text='One-line summary shown on the homepage tile.', max_length=160)),
                ('description', models.TextField(blank=True, help_text='Full description shown on the module detail page.')),
                ('demo_video', models.FileField(blank=True, help_text='Looping screen recording (MP4/WebM) shown on the detail page.', null=True, upload_to='modules/videos/')),
                ('thumbnail', models.ImageField(blank=True, help_text='Static preview image used as a fallback if no video is uploaded.', null=True, upload_to='modules/thumbs/')),
                ('industries', models.CharField(blank=True, help_text="Comma-separated industry tags, e.g. 'Retail, Restaurants, Hospitality'.", max_length=255)),
                ('demo_code', models.CharField(default='pos', max_length=40)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_featured', models.BooleanField(default=True, help_text='Show on the homepage module grid.')),
                ('is_published', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
    ]