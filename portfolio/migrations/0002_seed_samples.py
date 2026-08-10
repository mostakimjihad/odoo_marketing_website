"""Seed sample clients and a couple of placeholder certifications.

Real data should be added via the Django admin.
"""
from django.db import migrations
from datetime import date


CLIENTS = [
    {
        'name': 'Mysoftheaven (BD) Ltd.',
        'industry': 'ERP Software / Government Tech',
        'website': 'https://mysoftheaven.com',
        'testimonial': 'Mostakim delivered our full ERP rollout — CRM, HRM, Accounts, and Project Management — ahead of schedule. Strong technical work and clear communication throughout.',
        'testimonial_author': 'Project Manager',
        'testimonial_role': 'Mysoftheaven (BD) Ltd.',
        'is_featured': True,
        'order': 1,
    },
    {
        'name': 'JanataWifi',
        'industry': 'Telecom / AI',
        'website': 'https://janatawifi.com',
        'testimonial': 'Built our browser-automation AI prototype end-to-end. Solid Git workflow and clean documentation — exactly what we needed.',
        'testimonial_author': 'Engineering Lead',
        'testimonial_role': 'JanataWifi',
        'is_featured': True,
        'order': 2,
    },
]


CERTIFICATIONS = [
    {
        'title': 'Odoo Functional Certification',
        'issuer': 'Odoo',
        'issue_date': date(2024, 6, 1),
        'description': 'Demonstrates proficiency in Odoo business workflows across Sales, Purchase, Inventory, Accounting, and Manufacturing.',
        'order': 1,
    },
    {
        'title': 'Odoo Technical Certification',
        'issuer': 'Odoo',
        'issue_date': date(2024, 9, 1),
        'description': 'Validates expertise in Odoo module development, ORM, views, security, and deployment.',
        'order': 2,
    },
]


def seed_clients(apps, schema_editor):
    Client = apps.get_model('portfolio', 'Client')
    for c in CLIENTS:
        Client.objects.get_or_create(name=c['name'], defaults=c)


def remove_clients(apps, schema_editor):
    Client = apps.get_model('portfolio', 'Client')
    Client.objects.filter(name__in=[c['name'] for c in CLIENTS]).delete()


def seed_certs(apps, schema_editor):
    Certification = apps.get_model('portfolio', 'Certification')
    for cert in CERTIFICATIONS:
        Certification.objects.get_or_create(title=cert['title'], defaults=cert)


def remove_certs(apps, schema_editor):
    Certification = apps.get_model('portfolio', 'Certification')
    Certification.objects.filter(title__in=[c['title'] for c in CERTIFICATIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_clients, remove_clients),
        migrations.RunPython(seed_certs, remove_certs),
    ]