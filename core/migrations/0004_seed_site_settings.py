"""Populate the SiteSettings singleton with content derived from the CV."""
from django.db import migrations


ABOUT_BODY = """I'm an ERP engineer and systems builder with 12 years of experience across business content writing, frontend development, and Odoo/ERPNext engineering. I help companies replace fragmented spreadsheets, disconnected tools, and manual handoffs with a single, integrated ERP that runs the entire business — sales, inventory, accounting, manufacturing, HR, and customer operations on one data layer.

What I do goes past installing modules. I design the data model, write the integrations, automate the workflows, and ship the dashboards that turn operations into decisions. External payment gateways, eCommerce storefronts, third-party logistics, banks, BI tools — if it needs to talk to your ERP, I make it talk.

I hold a B.Sc. in Computer Science & Engineering from Green University of Bangladesh (CGPA 3.61/4.00), and I'm the author of a conference paper presented at DCOSS-IoT 2024 in Abu Dhabi on Quality-of-Experience aware task offloading in vehicular edge computing.

Whether you need a small business ERP rollout or a deep multi-system overhaul, I bring the same disciplined approach: clear scope, clean code, and honest communication."""


def populate_site_settings(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    obj, _ = SiteSettings.objects.get_or_create(pk=1)
    obj.about_body = ABOUT_BODY
    obj.hero_title = "Odoo & ERP Engineer for Hire"
    obj.hero_subtitle = (
        "Strong ERP engineering, full-stack integrations, and the writing "
        "to translate operational chaos into a working system."
    )
    obj.tagline = "Senior ERP & Odoo Engineer · 12 yrs building business systems"
    obj.full_name = "Mostakim Jihad"
    obj.linkedin = "https://www.linkedin.com/in/mostakimjihad"
    obj.github = "https://github.com/mostakimjihad"
    obj.codeforces = "https://codeforces.com/profile/mostakimjihad"
    obj.fiverr_url = "https://www.fiverr.com/mostakimjihad"
    obj.save()


def reset_site_settings(apps, schema_editor):
    # Leave defaults; do not delete the row to keep the singleton intact.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_seed_services'),
    ]
    operations = [
        migrations.RunPython(populate_site_settings, reset_site_settings),
    ]
