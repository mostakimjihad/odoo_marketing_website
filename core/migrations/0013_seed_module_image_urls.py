"""Populate ERPModule.image_url with curated Unsplash photos per module.

Each photo is a stable Unsplash image (images.unsplash.com/photo-{id})
matching the module's theme — analytics, retail, warehouse, factory, etc.
The template renders this image inside the browser-frame chrome; if the
URL is empty, the existing built-in mockup is shown instead.
"""
from django.db import migrations


# Stable Unsplash photo IDs picked for each module's theme.
# Querystring: w=800 for retina, q=80, auto=format, fit=crop.
URL_TEMPLATE = "https://images.unsplash.com/{photo}?w=800&q=80&auto=format&fit=crop"


MODULE_PHOTOS = {
    # Sales
    "sales":                 "photo-1556761175-5973dc0f32e7",  # business meeting
    "crm":                   "photo-1542744173-8e7e53415bb0",  # analytics chart
    "point-of-sale":         "photo-1556742049-0cfed4f6a45d",  # mobile checkout
    "ecommerce":             "photo-1557804506-669a67965ba0",  # online shopping
    "subscriptions":         "photo-1573497019418-b400bb3ab074",  # handshake / deal
    # Operations
    "purchase":              "photo-1556761175-4b46a572b786",  # paperwork / graphs
    "inventory":             "photo-1542838132-92c53300491e",  # warehouse boxes
    "manufacturing":         "photo-1565793298595-6a879b1d9492",  # factory line
    "field-service":         "photo-1581094288338-2314dddb7ece",  # technician
    "quality-maintenance":   "photo-1581094794329-c8112a89af12",  # inspection
    # Finance
    "accounting":            "photo-1551288049-bebda4e38f71",  # dashboard charts
    "expenses-approvals":    "photo-1554224155-6726b3ff858f",  # calculator / coins
    # People
    "human-resources":       "photo-1522071820081-009f0129c71c",  # team meeting
    # Web
    "website":               "photo-1460925895917-afdab827c52f",  # laptop / charts
    "marketing-automation":  "photo-1556761175-b413da4baf72",  # marketing analytics
    # Productivity
    "project":               "photo-1454165804606-c3d57bc86b40",  # planning / laptop
    "helpdesk":              "photo-1556761175-129418cb2dfe",  # support chat
}


def seed_image_urls(apps, schema_editor):
    ERPModule = apps.get_model('core', 'ERPModule')
    for module in ERPModule.objects.all():
        photo = MODULE_PHOTOS.get(module.slug)
        if photo:
            module.image_url = URL_TEMPLATE.format(photo=photo)
            module.save(update_fields=["image_url"])


def remove_image_urls(apps, schema_editor):
    ERPModule = apps.get_model('core', 'ERPModule')
    ERPModule.objects.all().update(image_url="")


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_add_erpmodule_image_url'),
    ]
    operations = [
        migrations.RunPython(seed_image_urls, remove_image_urls),
    ]
