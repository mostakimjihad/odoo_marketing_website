from django.db import migrations


MODULES = [
    {
        'slug': 'sales',
        'name': 'Sales',
        'short_tag': 'SALE',
        'category': 'sales',
        'tagline': 'Quotations to signed orders to invoices — one continuous chain.',
        'demo_code': 'crm',
        'industries': 'B2B, Wholesale, Services, Distribution',
        'order': 1,
        'description': (
            'Odoo Sales turns a quotation into a confirmed order, a delivery, and an '
            'invoice without anyone retyping a line. Customers can accept and sign '
            'quotations online, and upsells / optional products are one click away.\n\n'
            'I set up quotation templates, product pricelists, discount policies, '
            'delivery terms, online signature and payment, and the automation that '
            'pushes a won order into inventory and accounting.'
        ),
    },
    {
        'slug': 'purchase',
        'name': 'Purchase',
        'short_tag': 'PUR',
        'category': 'operations',
        'tagline': 'Reorder rules raise the RFQ before you run out of stock.',
        'demo_code': 'purchase',
        'industries': 'Retail, Manufacturing, Distribution, Restaurants',
        'order': 5,
        'description': (
            'Odoo Purchase automates replenishment: when stock crosses its reorder '
            'point, a request for quotation is drafted for the right vendor at the '
            'right price. Confirm it and the receipt and vendor bill are already '
            'waiting, matched line by line.\n\n'
            'I configure vendor pricelists, blanket orders, multi-vendor comparison, '
            'purchase agreements, approval limits, and 3-way matching between the '
            'purchase order, the receipt, and the bill.'
        ),
    },
    {
        'slug': 'inventory',
        'name': 'Inventory',
        'short_tag': 'STOCK',
        'category': 'operations',
        'tagline': 'Real stock levels across every warehouse, lot, and serial number.',
        'demo_code': 'inventory',
        'industries': 'Retail, Warehousing, Manufacturing, Pharma, Food',
        'order': 6,
        'description': (
            'Odoo Inventory uses double-entry stock moves — every unit that leaves one '
            'location arrives in another, so quantities are always explainable. Run '
            'multi-warehouse, multi-step receipts and deliveries, and trace any lot '
            'from vendor to customer.\n\n'
            'I implement barcode picking and putaway, storage strategies, reordering '
            'rules, lot / serial traceability, landed costs, inventory valuation '
            '(FIFO / AVCO) and the accounting entries behind them.'
        ),
    },
    {
        'slug': 'project',
        'name': 'Project & Timesheets',
        'short_tag': 'PROJ',
        'category': 'productivity',
        'tagline': 'Plan tasks, log hours, and bill the time you actually worked.',
        'demo_code': 'project',
        'industries': 'Agencies, Consultancies, Software, Construction',
        'order': 10,
        'description': (
            'Odoo Project gives every job a kanban board, deadlines, and a running '
            'timesheet. Hours logged against a task roll straight into a customer '
            'invoice when the project is billable.\n\n'
            'I configure project stages, task templates, planning and capacity views, '
            'timesheet approval flows, and billing rules for time-and-material or '
            'fixed-price engagements.'
        ),
    },
    {
        'slug': 'website',
        'name': 'Website & CMS',
        'short_tag': 'WEB',
        'category': 'web',
        'tagline': 'A site built on your live business data, not a disconnected CMS.',
        'demo_code': 'website',
        'industries': 'Any business with a public site',
        'order': 11,
        'description': (
            'Odoo Website is a drag-and-drop builder that reads from the same database '
            'as sales, inventory, and events. Forms create real leads, product pages '
            'show real stock, and the blog and SEO tools are built in.\n\n'
            'I build multi-page sites, custom themes and snippets, lead-capture forms '
            'wired into CRM, multi-language pages, and SEO / speed optimisation.'
        ),
    },
    {
        'slug': 'helpdesk',
        'name': 'Helpdesk & Support',
        'short_tag': 'HELP',
        'category': 'productivity',
        'tagline': 'Tickets, SLAs, and a customer portal that keeps clients informed.',
        'demo_code': 'helpdesk',
        'industries': 'SaaS, IT services, After-sales support',
        'order': 12,
        'description': (
            'Odoo Helpdesk turns emails, portal submissions, and live chat into tracked '
            'tickets with SLA policies and escalation. Customers follow progress in the '
            'portal instead of chasing you by phone.\n\n'
            'I set up teams, ticket stages, SLA rules, canned responses, knowledge base '
            'articles, and integration with sales orders so support sees what the '
            'customer actually bought.'
        ),
    },
    {
        'slug': 'field-service',
        'name': 'Field Service',
        'short_tag': 'FSM',
        'category': 'operations',
        'tagline': 'Dispatch technicians, track parts used, and invoice on site.',
        'demo_code': 'field-service',
        'industries': 'Installation, Repairs, Maintenance contracts',
        'order': 13,
        'description': (
            'Odoo Field Service plans on-site jobs, gives technicians a mobile worksheet, '
            'and records the parts and hours consumed so the invoice is accurate the '
            'first time.\n\n'
            'I configure scheduling and dispatch, mobile worksheets with customer '
            'signature, product consumption from van stock, and recurring maintenance '
            'visits.'
        ),
    },
    {
        'slug': 'subscriptions',
        'name': 'Subscriptions',
        'short_tag': 'SUBS',
        'category': 'sales',
        'tagline': 'Recurring revenue billed automatically, with churn you can see.',
        'demo_code': 'subscriptions',
        'industries': 'SaaS, Memberships, Service retainers',
        'order': 14,
        'description': (
            'Odoo Subscriptions handles recurring plans: automatic invoicing, online '
            'payment tokens, upgrades and downgrades mid-cycle, and MRR / churn '
            'reporting.\n\n'
            'I set up subscription templates, prorated upsells, dunning for failed '
            'payments, renewal alerts, and the revenue reports leadership asks for.'
        ),
    },
    {
        'slug': 'marketing-automation',
        'name': 'Marketing Automation',
        'short_tag': 'MKT',
        'category': 'web',
        'tagline': 'Email, SMS, and campaign flows triggered by what customers do.',
        'demo_code': 'marketing',
        'industries': 'eCommerce, B2B lead gen, Events',
        'order': 15,
        'description': (
            'Odoo Marketing Automation builds drip campaigns on top of your real CRM and '
            'sales data — segment by purchase history, trigger on behaviour, and stop '
            'the sequence when a lead converts.\n\n'
            'I design campaign workflows, email and SMS templates, lead scoring, A/B '
            'tests, and attribution reporting back to closed revenue.'
        ),
    },
    {
        'slug': 'quality-maintenance',
        'name': 'Quality & Maintenance',
        'short_tag': 'QC',
        'category': 'operations',
        'tagline': 'Inline quality checks and preventive maintenance on your equipment.',
        'demo_code': 'quality',
        'industries': 'Manufacturing, Food, Pharma, Heavy industry',
        'order': 16,
        'description': (
            'Odoo Quality inserts control points into receipts, manufacturing, and '
            'deliveries so defects are caught where they happen. Maintenance schedules '
            'preventive work on machines and logs every breakdown.\n\n'
            'I configure quality control points, measurement tolerances, alerts and '
            'non-conformance handling, plus preventive maintenance calendars and MTBF '
            'reporting.'
        ),
    },
    {
        'slug': 'expenses-approvals',
        'name': 'Expenses & Approvals',
        'short_tag': 'EXP',
        'category': 'people',
        'tagline': 'Snap a receipt, get it approved, get reimbursed on payroll.',
        'demo_code': 'expenses',
        'industries': 'Any team with field or travel spend',
        'order': 17,
        'description': (
            'Odoo Expenses lets staff submit a receipt from their phone. Managers approve '
            'in one screen, finance posts it to the right account, and reimbursement '
            'goes out with payroll or as a direct payment.\n\n'
            'I set up expense categories and limits, multi-level approval rules, '
            'company-card reconciliation, and the generic Approvals app for anything '
            'else that needs a sign-off.'
        ),
    },
]


def seed(apps, schema_editor):
    ERPModule = apps.get_model('core', 'ERPModule')
    for data in MODULES:
        payload = dict(data)
        slug = payload.pop('slug')
        payload['is_featured'] = True
        payload['is_published'] = True
        ERPModule.objects.update_or_create(slug=slug, defaults=payload)

    # Keep the original six ahead of the new ones in the grid.
    order_fix = {
        'crm': 2,
        'point-of-sale': 3,
        'ecommerce': 4,
        'manufacturing': 7,
        'accounting': 8,
        'human-resources': 9,
    }
    for slug, order in order_fix.items():
        ERPModule.objects.filter(slug=slug).update(order=order)


def unseed(apps, schema_editor):
    ERPModule = apps.get_model('core', 'ERPModule')
    ERPModule.objects.filter(slug__in=[m['slug'] for m in MODULES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_quotelead'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
