"""Populate the SiteSettings singleton with content derived from the CV."""
from django.db import migrations


ABOUT_BODY = """I'm a Jr. Software Engineer specializing in Odoo, ERPNext, and Python-based ERP solutions. Currently I work at Mysoftheaven (BD) Ltd., where I've delivered a full-scale ERP rollout covering CRM, HRM, Accounts, and Project Management — plus a Bangla chatbot for the government project LDTax.

Before this, I interned as an AI Engineer at JanataWifi, building browser-automation agents on Azure OpenAI and LangChain. That experience sharpened my ability to ship production-quality software under tight deadlines.

I hold a B.Sc. in Computer Science & Engineering from Green University of Bangladesh (CGPA 3.61/4.00), and I'm the author of a conference paper presented at DCOSS-IoT 2024 in Abu Dhabi on Quality-of-Experience aware task offloading in vehicular edge computing.

Whether you need a small business ERP rollout or a deep custom module for Odoo Community, I bring the same disciplined engineering approach: clear scope, clean code, and honest communication."""


def populate_site_settings(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    obj, _ = SiteSettings.objects.get_or_create(pk=1)
    obj.about_body = ABOUT_BODY
    obj.hero_title = "Odoo & ERP Expert for Hire"
    obj.hero_subtitle = (
        "From small-business ERP rollouts to complex custom modules — "
        "I deliver clean, reliable Odoo solutions that fit your business."
    )
    obj.tagline = "Jr. Software Engineer · Odoo & ERPNext Specialist"
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
        ('core', '0002_seed_services'),
    ]
    operations = [
        migrations.RunPython(populate_site_settings, reset_site_settings),
    ]