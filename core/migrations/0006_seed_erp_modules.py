from django.db import migrations
from django.utils.text import slugify


MODULES = [
    {
        'name': 'Point of Sale',
        'short_tag': 'POS',
        'category': 'sales',
        'tagline': 'Process sales, accept payments, and manage inventory from any device.',
        'demo_code': 'pos',
        'industries': 'Retail, Restaurants, Cafés, Pop-up shops',
        'order': 1,
        'description': (
            'Odoo Point of Sale is a fast, touch-friendly checkout that works on any device — '
            'desktop, tablet, or phone. It runs offline, syncs automatically when reconnected, '
            'and links every sale to your inventory and accounting in real time.\n\n'
            'I implement POS for retail stores, cafés, and multi-branch operations — including '
            'cash drawer / receipt printer integration, barcode scanning, customer displays, '
            'loyalty programs, and end-of-day reconciliation.'
        ),
    },
    {
        'name': 'Accounting',
        'short_tag': 'ACC',
        'category': 'finance',
        'tagline': 'Invoicing, bank sync, and reporting that stays accurate automatically.',
        'demo_code': 'accounting',
        'industries': 'Services, Agencies, Wholesale, SaaS',
        'order': 2,
        'description': (
            'Odoo Accounting replaces spreadsheets with a double-entry ledger that imports '
            'bank statements, reconciles payments, and generates VAT / sales tax reports '
            'out of the box.\n\n'
            'I configure chart of accounts, tax mappings (BD, EU, US, GCC), customer/supplier '
            'payment terms, automated bank reconciliation, and multi-currency handling. '
            'You get clean books at month-end without manual data entry.'
        ),
    },
    {
        'name': 'Manufacturing',
        'short_tag': 'MRP',
        'category': 'operations',
        'tagline': 'Plan work orders, track components, and run your shop floor from one screen.',
        'demo_code': 'mrp',
        'industries': 'Manufacturing, Assembly, Furniture, Food production',
        'order': 3,
        'description': (
            'Odoo Manufacturing (MRP) lets you turn sales orders into work orders, generate '
            'bills of materials, schedule operations on work centers, and track real-time '
            'progress against capacity.\n\n'
            'I set up BOMs, routing, work center capacity planning, by-product handling, '
            'quality checks, and integration with inventory and purchasing so raw materials '
            'replenish automatically when work orders start.'
        ),
    },
    {
        'name': 'Human Resources',
        'short_tag': 'HR',
        'category': 'people',
        'tagline': 'Employees, attendance, payroll, and leave — all in one place.',
        'demo_code': 'hr',
        'industries': 'Any team of 5+',
        'order': 4,
        'description': (
            'Odoo HR centralizes employee records, attendance, leave requests, expense '
            'reports, and payslip generation. Employees self-serve through the portal; '
            'managers approve in one click.\n\n'
            'I configure departments, contracts, salary structures, leave allocations, '
            'attendance rules, and integrate with payroll providers for your country.'
        ),
    },
    {
        'name': 'eCommerce',
        'short_tag': 'eCom',
        'category': 'sales',
        'tagline': 'A storefront that shares inventory and customers with your backend.',
        'demo_code': 'ecommerce',
        'industries': 'B2C retail, DTC brands, B2B catalogs',
        'order': 5,
        'description': (
            'Odoo eCommerce is built on the same database as your inventory and accounting. '
            'Sell on a customizable storefront, sync stock in real time, ship with integrated '
            'carriers, and process returns without manual updates.\n\n'
            'I build storefronts with product variants, multi-currency pricing, tax rules '
            'per region, payment gateways (Stripe / PayPal / bKash / SSLCommerz), and '
            'integrations with shipping providers.'
        ),
    },
    {
        'name': 'CRM',
        'short_tag': 'CRM',
        'category': 'sales',
        'tagline': 'Track leads, automate follow-ups, and forecast revenue accurately.',
        'demo_code': 'crm',
        'industries': 'B2B sales, Real estate, Services',
        'order': 6,
        'description': (
            'Odoo CRM gives sales teams a visual pipeline, automated activity scheduling, '
            'and integrated email / phone — so every touchpoint is logged against the right '
            'opportunity.\n\n'
            'I configure sales teams, lead scoring rules, quotation templates, automated '
            'follow-ups, and reports that give leadership real-time pipeline visibility.'
        ),
    },
]


def seed(apps, schema_editor):
    ERPModule = apps.get_model('core', 'ERPModule')
    for data in MODULES:
        ERPModule.objects.update_or_create(
            slug=slugify(data['name']),
            defaults={
                'name': data['name'],
                'short_tag': data['short_tag'],
                'category': data['category'],
                'tagline': data['tagline'],
                'demo_code': data['demo_code'],
                'industries': data['industries'],
                'description': data['description'],
                'order': data['order'],
                'is_featured': True,
                'is_published': True,
            },
        )


def unseed(apps, schema_editor):
    ERPModule = apps.get_model('core', 'ERPModule')
    for data in MODULES:
        ERPModule.objects.filter(slug=slugify(data['name'])).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_erpmodule'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]