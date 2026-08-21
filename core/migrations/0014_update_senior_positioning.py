"""Update the SiteSettings singleton to senior positioning.

Removes "Jr. Software Engineer" framing, refreshes the tagline and
about_body to reflect 12 years of experience across business content
writing, frontend development, and ERP engineering, and bumps the
years_experience / projects_completed / happy_clients counters to match.
"""
from django.db import migrations


NEW_ABOUT_BODY = """I'm an ERP engineer and systems builder with 12 years of experience across business content writing, frontend development, and Odoo/ERPNext engineering. I help companies replace fragmented spreadsheets, disconnected tools, and manual handoffs with a single, integrated ERP that runs the entire business — sales, inventory, accounting, manufacturing, HR, and customer operations on one data layer.

What I do goes past installing modules. I design the data model, write the integrations, automate the workflows, and ship the dashboards that turn operations into decisions. External payment gateways, eCommerce storefronts, third-party logistics, banks, BI tools — if it needs to talk to your ERP, I make it talk.

I hold a B.Sc. in Computer Science & Engineering from Green University of Bangladesh (CGPA 3.61/4.00), and I'm the author of a conference paper presented at DCOSS-IoT 2024 in Abu Dhabi on Quality-of-Experience aware task offloading in vehicular edge computing.

Whether you need a small business ERP rollout or a deep multi-system overhaul, I bring the same disciplined approach: clear scope, clean code, and honest communication."""


NEW_TAGLINE = "Senior ERP & Odoo Engineer · 12 yrs building business systems"

NEW_HERO_TITLE = "Odoo & ERP Engineer for Hire"
NEW_HERO_SUBTITLE = (
    "Strong ERP engineering, full-stack integrations, and the writing "
    "to translate operational chaos into a working system."
)


def update_positioning(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    obj, _ = SiteSettings.objects.get_or_create(pk=1)
    obj.about_body = NEW_ABOUT_BODY
    obj.tagline = NEW_TAGLINE
    obj.hero_title = NEW_HERO_TITLE
    obj.hero_subtitle = NEW_HERO_SUBTITLE
    if obj.years_experience < 12:
        obj.years_experience = 12
    if obj.projects_completed < 80:
        obj.projects_completed = 80
    if obj.happy_clients < 40:
        obj.happy_clients = 40
    obj.save()


def revert_positioning(apps, schema_editor):
    # No-op: we don't want to silently regress the live copy.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0013_seed_module_image_urls'),
    ]
    operations = [
        migrations.RunPython(update_positioning, revert_positioning),
    ]
