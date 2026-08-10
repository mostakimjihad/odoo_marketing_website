"""Seed the 11 services from the project brief."""
from django.db import migrations
from django.utils.text import slugify


SERVICES = [
    {
        'title': 'Small ERP Implementation',
        'short_description': 'End-to-end ERP setup for small businesses — modules, workflows, and user training.',
        'icon': 'apps.svg',
        'description': (
            "I help small businesses roll out their first ERP system without the headaches of "
            "over-engineering. From selecting the right modules to configuring your workflows, "
            "I deliver a system your team will actually use."
        ),
        'features': [
            'Module selection & scope planning',
            'Workflow configuration',
            'Data import (customers, vendors, products)',
            'User roles & access rights setup',
            'Hands-on training for your team',
            'Post-go-live support',
        ],
        'order': 1,
    },
    {
        'title': 'Odoo Community ERP Implementation',
        'short_description': 'Full Odoo Community setup — installation, configuration, and production deployment.',
        'icon': 'base_icon.svg',
        'description': (
            "Odoo Community is a powerful open-source ERP. I'll set it up correctly the first time: "
            "secure deployment, production-grade database, custom modules, and integrations tailored "
            "to your business."
        ),
        'features': [
            'Odoo installation & deployment',
            'Database design & migration',
            'Custom module development',
            'Third-party integrations',
            'Performance tuning',
            'Ongoing maintenance',
        ],
        'order': 2,
    },
    {
        'title': 'Data Migration',
        'short_description': 'Move your data from spreadsheets, legacy software, or older ERP versions safely.',
        'icon': 'data_recycle.svg',
        'description': (
            "Whether you're switching from Tally, QuickBooks, ERPNext, or just messy spreadsheets — "
            "I migrate your data cleanly with field mapping, validation, and zero-downtime cuts."
        ),
        'features': [
            'Legacy system analysis',
            'Field mapping & transformation',
            'Data cleansing & deduplication',
            'Test runs in staging',
            'Zero-downtime cutover',
            'Post-migration reconciliation',
        ],
        'order': 3,
    },
    {
        'title': 'Version Migration',
        'short_description': 'Upgrade Odoo from older versions to the latest stable release without losing data.',
        'icon': 'settings.svg',
        'description': (
            "Upgrading Odoo can break custom modules and workflows. I handle end-to-end version "
            "upgrades — code migration, data preservation, regression testing, and re-deployment."
        ),
        'features': [
            'Pre-upgrade audit & compatibility check',
            'Custom module migration to new API',
            'Database upgrade',
            'Full regression testing',
            'Documentation of breaking changes',
            'Rollback plan if needed',
        ],
        'order': 4,
    },
    {
        'title': 'Custom Feature Development',
        'short_description': 'New modules, fields, reports, and business logic — built exactly to your spec.',
        'icon': 'web_studio.svg',
        'description': (
            "Need a feature Odoo doesn't ship with? I build custom modules — from a single new field "
            "and workflow to a full multi-app feature. Clean code, proper tests, full documentation."
        ),
        'features': [
            'Requirements analysis',
            'Module architecture design',
            'Backend + frontend development',
            'Unit & integration tests',
            'Documentation',
            'Maintenance & enhancements',
        ],
        'order': 5,
    },
    {
        'title': 'Functional Consultancy',
        'short_description': 'Process analysis, best-practice recommendations, and Odoo readiness assessment.',
        'icon': 'industry_odoo_partner.svg',
        'description': (
            "Not sure if Odoo fits your business? I run discovery sessions, map your processes, and "
            "give you an honest recommendation — including scope, timeline, and budget ranges."
        ),
        'features': [
            'Business process mapping',
            'Gap analysis',
            'Odoo readiness assessment',
            'Module selection guidance',
            'ROI estimation',
            'Implementation roadmap',
        ],
        'order': 6,
    },
    {
        'title': 'Run Odoo Server',
        'short_description': 'Hosting, monitoring, backups, and day-to-day management of your Odoo instance.',
        'icon': 'maintenance.svg',
        'description': (
            "I'll run your Odoo server so you can focus on your business. Production-grade hosting, "
            "automated backups, performance monitoring, and on-demand support."
        ),
        'features': [
            'Cloud or on-premise hosting',
            'Daily automated backups',
            'Uptime & performance monitoring',
            'Security patches & updates',
            'SSL certificate management',
            'On-demand support hours',
        ],
        'order': 7,
    },
    {
        'title': 'Deployment',
        'short_description': 'CI/CD pipelines, Docker, and production-grade deployment for Odoo.',
        'icon': 'iot.svg',
        'description': (
            "Stop deploying manually. I set up Docker-based deployments with CI/CD so every change "
            "is tested and deployed automatically — reliable, repeatable, recoverable."
        ),
        'features': [
            'Docker & docker-compose setup',
            'CI/CD pipelines (GitHub Actions / GitLab CI)',
            'Staging + production environments',
            'Zero-downtime deployments',
            'Rollback automation',
            'SSL & reverse proxy (Nginx/Caddy)',
        ],
        'order': 8,
    },
    {
        'title': 'Odoo Server Optimization',
        'short_description': 'Speed up slow Odoo instances — workers, caching, PostgreSQL tuning, indexing.',
        'icon': 'spreadsheet_dashboard.svg',
        'description': (
            "Is your Odoo slow? I diagnose and fix performance bottlenecks across the stack — "
            "workers, PostgreSQL, NGINX, cron jobs, and module-level inefficiencies."
        ),
        'features': [
            'Performance profiling',
            'Worker tuning (CPU/memory)',
            'PostgreSQL query optimization',
            'Caching strategy (Redis, in-memory)',
            'Asset & asset bundling cleanup',
            'Benchmark before/after',
        ],
        'order': 9,
    },
    {
        'title': 'Bug Fix in Existing Software',
        'short_description': 'Diagnose and fix bugs in Odoo, ERPNext, or custom Python/Django code.',
        'icon': 'repair.svg',
        'description': (
            "Stuck on a bug that's blocking your team? I triage fast, find the root cause, and "
            "deliver a tested fix — with a write-up so you know what happened and how to prevent it."
        ),
        'features': [
            'Bug triage & reproduction',
            'Root-cause analysis',
            'Code fix with tests',
            'Regression test coverage',
            'Incident postmortem',
            'Prevention recommendations',
        ],
        'order': 10,
    },
    {
        'title': 'Performance Enhancement',
        'short_description': 'Make existing Odoo or Django apps faster, leaner, and more scalable.',
        'icon': 'quality_control.svg',
        'description': (
            "Beyond bug fixes — I'll profile your existing application, identify the slowest parts, "
            "and ship measurable improvements with benchmarks to prove the gains."
        ),
        'features': [
            'Full-stack profiling',
            'Database query optimization',
            'N+1 query elimination',
            'Caching layer implementation',
            'Frontend bundle optimization',
            'Before/after benchmark report',
        ],
        'order': 11,
    },
]


def seed_services(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    for s in SERVICES:
        Service.objects.get_or_create(
            title=s['title'],
            defaults={
                'slug': slugify(s['title']),
                'short_description': s['short_description'],
                'icon': s['icon'],
                'description': s['description'],
                'features': '\n'.join(s['features']),
                'order': s['order'],
                'is_active': True,
            },
        )


def remove_services(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    Service.objects.filter(title__in=[s['title'] for s in SERVICES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_services, remove_services),
    ]