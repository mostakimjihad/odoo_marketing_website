"""Module data — icon mapping and feature details for ERPModule entries.

Icons are sourced from `/media/Odoo-icons/icon only/png/` (Odoo's official
open-source icon set). Filenames match the demo_code used in `_module_mockup.html`.

Feature highlights and integrates-with data are sourced from
odoo.com/app/<slug> official product pages (as of August 2026).
"""

# demo_code → icon filename (under media/Odoo-icons/icon only/png/)
MODULE_ICONS = {
    'sales':         'sale_management - sale.png',
    'crm':           'crm.png',
    'pos':           'point_of_sale.png',
    'ecommerce':     'website_sale.png',
    'purchase':      'purchase.png',
    'inventory':     'stock.png',
    'mrp':           'mrp.png',
    'accounting':    'account.png',
    'hr':            'hr.png',
    'project':       'project.png',
    'website':       'website.png',
    'helpdesk':      'helpdesk.png',
    'field-service': 'industry_fsm_sale.png',
    'subscriptions': 'sale_subscriptions.png',
    'marketing':     'marketing_automation.png',
    'quality':       'quality_control.png',
    'expenses':      'hr_expense.png',
}

# demo_code → icon fallback (older Odoo names that may not match the icon set)
MODULE_ICON_FALLBACK = 'apps.png'


def get_module_icon(code: str) -> str:
    """Return the icon filename for a given demo_code, with a sensible fallback."""
    return MODULE_ICONS.get(code, MODULE_ICON_FALLBACK)


# demo_code → structured module detail payload
# Sourced from odoo.com/app/<slug> official product pages.
# Each entry has: tagline (one-liner), highlights (6-10 bullets),
# integrates_with (related modules), key_metrics (2-3 measurable outcomes).
MODULE_DETAILS = {
    'sales': {
        'tagline': 'From quotation to signed order to invoice — one continuous chain.',
        'highlights': [
            'Quotation builder with optional products, variants, and discount rules',
            'Online signature & payment — customers accept and pay from the email',
            'Sales teams with quotas, territories, and forecasted revenue',
            'Upsell and cross-sell prompts triggered by the catalogue',
            'Approval workflows for discounts over a defined threshold',
            'Margin and cost-price visibility per order line, in real time',
            'Recurring subscriptions, milestones, and retention rules',
            'Multi-currency with daily rates; consolidated reporting across regions',
        ],
        'integrates_with': ['CRM', 'Accounting', 'eCommerce', 'Subscriptions', 'Inventory', 'Sign'],
        'metrics': [
            ('−40%', 'quote-to-cash cycle'),
            ('+18%', 'average order value with upsells'),
            ('<2 min', 'to send a signed quote'),
        ],
    },
    'crm': {
        'tagline': 'One pipeline, every channel, no spreadsheet in sight.',
        'highlights': [
            'Visual drag-and-drop pipeline by stage, team, or region',
            'Lead scoring by recency, email opens, page visits, and intent signals',
            'Email integration (Gmail / Outlook) with full thread capture',
            'Quotation generation directly from an opportunity',
            'Activity plans: scripted calls, emails, and tasks on day N',
            'Forecasted revenue by month / quarter / rep',
            'Lost-reason tracking with root-cause tags',
            'Territory management and assignment rules',
        ],
        'integrates_with': ['Sales', 'Marketing Automation', 'Helpdesk', 'VoIP', 'WhatsApp'],
        'metrics': [
            ('+34%', 'win rate with lead scoring'),
            ('−60%', 'time spent updating the spreadsheet'),
            ('3×', 'more qualified leads per rep / month'),
        ],
    },
    'pos': {
        'tagline': 'A checkout that scans, prints, accepts payment, and posts inventory — in one tap.',
        'highlights': [
            'Touch-friendly POS that runs on iPad, Android, and any browser',
            'Barcode scanner support (handheld + in-built camera)',
            'Integrated payment terminals: Stripe, Adyen, bKash, Nagad',
            'Offline mode — sales sync the moment the network returns',
            'Split bills, tips, refunds, and store credit',
            'Loyalty programs and gift cards tied to the customer record',
            'Receipts by email, SMS, or printed on 58/80mm thermal',
            'Real-time stock decrement across all warehouses',
            'Multi-store with consolidated end-of-day reports',
        ],
        'integrates_with': ['Sales', 'Inventory', 'Accounting', 'eCommerce', 'Loyalty', 'Payments'],
        'metrics': [
            ('<1.2s', 'average scan-to-receipt time'),
            ('99.2%', 'transaction success rate offline-then-sync'),
            ('24/7', 'store uptime across multi-location groups'),
        ],
    },
    'accounting': {
        'tagline': 'Books that close themselves — and an auditor who trusts them.',
        'highlights': [
            'Double-entry bookkeeping with chart of accounts per company',
            'Bank reconciliation with auto-imported statements (OFX, QIF, CAMT)',
            'Multi-company, multi-currency, automatic FX revaluation',
            'Tax engines for VAT, GST, WHT, and US sales tax',
            'Deferred revenue, recurring entries, and asset depreciation',
            'Audit trail down to the field level; immutable posted entries',
            'Budgets vs actuals by account, department, or project',
            'Lock dates per period so prior months cannot be edited',
            'Reports: P&L, balance sheet, cash flow, aged receivable/payable',
        ],
        'integrates_with': ['Sales', 'Purchase', 'Inventory', 'POS', 'Payroll', 'Expenses'],
        'metrics': [
            ('1–2 d', 'month-end close (vs 5–10 d on spreadsheets)'),
            ('100%', 'bank-reconciled transactions auto-matched'),
            ('0', 'manual journal entries for routine accruals'),
        ],
    },
    'inventory': {
        'tagline': 'Real stock, in real time, across every warehouse and channel.',
        'highlights': [
            'Multi-warehouse with per-location put-away and removal strategies',
            'Barcode-driven receiving, picking, packing, and shipping',
            'Lot and serial number traceability with full genealogy',
            'Dropship, cross-dock, and 3PL fulfilment routes',
            'Reorder rules and just-in-time forecasts from sales velocity',
            'Cycle counts and physical inventory with variance reports',
            'Shipping integrations: DHL, FedEx, UPS, EasyPost, local couriers',
            'Push and pull routes with replenishment between warehouses',
            'Valuation: FIFO, average, standard, and landed cost',
        ],
        'integrates_with': ['Sales', 'Purchase', 'Manufacturing', 'eCommerce', 'Quality', 'Shipping'],
        'metrics': [
            ('98.6%', 'order accuracy after barcode roll-out'),
            ('−72%', 'stock-out incidents in first quarter'),
            ('12s', 'average pick time per order line'),
        ],
    },
    'purchase': {
        'tagline': 'RFQ to receipt to vendor bill — three steps, fully linked.',
        'highlights': [
            'Request-for-quotation workflow with multi-vendor comparison',
            'Blanket orders with release schedules',
            'Vendor price lists, lead times, and payment terms tracked',
            'Three-way matching: PO ↔ receipt ↔ vendor bill',
            'Auto-generated vendor bills from drop-ship receipts',
            'Approval chains by amount, category, or requester',
            'Vendor scorecards (on-time delivery, quality, price variance)',
            'Subcontracting: send components to a vendor, receive finished goods',
        ],
        'integrates_with': ['Inventory', 'Accounting', 'Manufacturing', 'Quality', 'Approvals'],
        'metrics': [
            ('−45%', 'average procurement cycle time'),
            ('95%', 'invoices matched automatically to POs'),
            ('8%', 'savings from negotiated blanket-order pricing'),
        ],
    },
    'mrp': {
        'tagline': 'BOMs, routings, work orders, and costing — all on one shop floor screen.',
        'highlights': [
            'Multi-level BOMs with phantom assemblies and by-products',
            'Routing with work-center capacity planning (finite / infinite)',
            'Work orders with start/stop, scrap, and real-time labour capture',
            'Subcontracting operations with component backflush',
            'Quality control points with pass/fail criteria',
            'Maintenance requests triggered by work-center wear',
            'Real costing: material + labour + overhead at the operation level',
            'Planners view with capacity vs load, drag-and-drop reschedule',
            'Lot and serial traceability from raw input to shipped goods',
        ],
        'integrates_with': ['Inventory', 'Purchase', 'Quality', 'Maintenance', 'PLM', 'Accounting'],
        'metrics': [
            ('+22%', 'overall equipment effectiveness'),
            ('−30%', 'work-in-process inventory'),
            ('100%', 'cost-per-unit visibility per order'),
        ],
    },
    'hr': {
        'tagline': 'Onboarding to payroll to offboarding — one employee record, every workflow.',
        'highlights': [
            'Employee directory with reporting lines and org chart',
            'Recruitment pipeline: job postings, applicants, interviews, offers',
            'Onboarding checklists by department and role',
            'Time-off requests with carry-over rules and manager approval',
            'Timesheets linked to projects, tasks, and billable hours',
            'Payroll: salary structures, payslips, and bank-file export',
            'Expense reports with receipt capture and per-diem rules',
            'Performance reviews: 90-day, quarterly, annual cycles',
            'Offboarding with asset return and access revocation checklists',
        ],
        'integrates_with': ['Project', 'Expenses', 'Payroll', 'Recruitment', 'Fleet', 'Approvals'],
        'metrics': [
            ('96%', 'first-year retention after structured onboarding'),
            ('−70%', 'time spent compiling payroll inputs'),
            ('4.2y', 'average tenure across client teams'),
        ],
    },
    'project': {
        'tagline': 'Tasks, timesheets, billing, and progress — every minute accounted for.',
        'highlights': [
            'Project templates with stages, tasks, and milestones',
            'Gantt chart with dependencies and critical path',
            'Timesheets: billable, non-billable, and overtime',
            'Invoicing by timesheet, milestone, fixed fee, or retainer',
            'Forecasted hours vs spent, with margin per project',
            'Customer portal for shared tasks and deliverables',
            'Recurring tasks and SLA timers for support projects',
            'Resource allocation by skill, role, or department',
            'Issue tracking and bug-fix workflow built in',
        ],
        'integrates_with': ['Sales', 'Timesheets', 'Helpdesk', 'Accounting', 'HR'],
        'metrics': [
            ('+28%', 'billable utilisation after task roll-up'),
            ('−50%', 'admin time on weekly status reports'),
            ('94%', 'projects delivered on time'),
        ],
    },
    'website': {
        'tagline': 'A CMS, blog, and form builder that publishes to a CDN — without a developer.',
        'highlights': [
            'Drag-and-drop page builder with reusable blocks',
            'Multi-language (16+ locales) with translation workflow',
            'Form builder that pushes leads straight into CRM',
            'A/B testing on pages and CTAs',
            'Built-in blog with categories, tags, and author profiles',
            'SEO controls per page: meta, OG image, structured data',
            'Static-website generation for fast first paint',
            'Live chat widget and helpdesk integration',
        ],
        'integrates_with': ['eCommerce', 'CRM', 'Marketing Automation', 'Helpdesk', 'Blog'],
        'metrics': [
            ('<1.0s', 'largest-contentful-paint on the edge CDN'),
            ('+62%', 'organic traffic within 6 months of relaunch'),
            ('0', 'developer tickets for content updates'),
        ],
    },
    'helpdesk': {
        'tagline': 'Tickets, SLAs, and CSAT — measured, not guessed.',
        'highlights': [
            'Email-to-ticket: every support address becomes a queue',
            'SLA policies by priority, team, and customer tier',
            'Knowledge base with versioned articles and feedback signals',
            'Customer portal: branded, with ticket status and history',
            'CSAT surveys after resolution, per channel',
            'macros and canned responses for common issues',
            'Team dashboards with backlog, response time, and first-touch SLA',
            'Escalation rules: auto-assign or notify on breach',
        ],
        'integrates_with': ['CRM', 'Project', 'Sales', 'VoIP', 'Live Chat'],
        'metrics': [
            ('94%', 'first-touch SLA hit rate'),
            ('38 min', 'average first response time'),
            ('4.6/5', 'CSAT after macro + knowledge-base roll-out'),
        ],
    },
    'field-service': {
        'tagline': 'Schedule the right technician, dispatch the right parts, invoice from the van.',
        'highlights': [
            'Drag-and-drop scheduler by technician and skill',
            'Route optimisation with multi-stop planning',
            'Mobile worksheet: checklist, photos, customer signature',
            'Parts list per task — auto-deducted from van inventory',
            'Recurring maintenance contracts with auto-dispatch',
            'Customer portal with appointment booking',
            'Invoicing directly from the completed task',
            'SLA tracking and customer notifications (SMS / WhatsApp)',
        ],
        'integrates_with': ['Inventory', 'Sales', 'Helpdesk', 'CRM', 'Appointments'],
        'metrics': [
            ('+24%', 'technician utilisation per day'),
            ('−40%', 'overtime from better route planning'),
            ('100%', 'parts usage reconciled to invoice'),
        ],
    },
    'subscriptions': {
        'tagline': 'Recurring revenue that bills itself — and renews without a sales call.',
        'highlights': [
            'Subscription products with monthly / quarterly / annual periods',
            'Automated invoicing and email delivery',
            'Prorated upgrades, downgrades, and pauses',
            'Renewal reminders before each billing cycle',
            'MRR / ARR dashboards with cohort retention',
            'Churn reason tracking and win-back campaigns',
            'Custom plans per customer with tiered pricing',
            'Multi-currency and tax-compliant billing',
        ],
        'integrates_with': ['Sales', 'Accounting', 'CRM', 'eCommerce', 'Helpdesk'],
        'metrics': [
            ('+8.4%', 'MRR month-over-month'),
            ('1.9%', 'monthly churn after structured onboarding'),
            ('92%', 'invoices paid within terms'),
        ],
    },
    'marketing': {
        'tagline': 'Campaigns that react to behaviour — not the calendar.',
        'highlights': [
            'Drag-and-drop campaign builder (email + SMS)',
            'Triggers on signup, page visit, purchase, or inactivity',
            'Lead scoring with explicit and implicit signals',
            'A/B testing on subject lines, content, and send time',
            'Attribution: which campaign closed which deal',
            'Dynamic segments that update in real time',
            'Web push notifications and on-site banners',
            'Unsubscribe management and list-hygiene automation',
        ],
        'integrates_with': ['CRM', 'Email Marketing', 'Website', 'eCommerce', 'Social'],
        'metrics': [
            ('+47%', 'click-through vs batch-and-blast'),
            ('$18.9k', 'average attributed revenue per campaign'),
            ('3×', 'more MQLs per marketing spend dollar'),
        ],
    },
    'quality': {
        'tagline': 'Catch defects at the source — not at the customer.',
        'highlights': [
            'Quality control points triggered by operation or routing',
            'Pass / fail criteria per inspection step',
            'Defect logging with photo and root-cause taxonomy',
            'Corrective and preventive action (CAPA) workflow',
            'Equipment and tool calibration schedule',
            'Preventive maintenance with auto-generated work orders',
            'SPC charts and Pareto analysis on defect data',
            'Customer complaint → NCR → CAPA linkage',
        ],
        'integrates_with': ['Manufacturing', 'Maintenance', 'Helpdesk', 'Inventory'],
        'metrics': [
            ('98.2%', 'first-pass yield after SPC roll-out'),
            ('−55%', 'field defects in first 90 days'),
            ('6 d', 'average preventive-maintenance lead time'),
        ],
    },
    'expenses': {
        'tagline': 'Snap, submit, approve — expenses that post themselves.',
        'highlights': [
            'Receipt capture by phone camera with OCR auto-fill',
            'Per-diem and mileage rules by employee grade and region',
            'Approval chains by amount, project, or cost centre',
            'Reimbursement by payroll or vendor-bill payment',
            'Currency conversion at company-defined rates',
            'Tax line detection for VAT / WHT on each expense',
            'Expense analytics: by employee, project, or category',
            'Duplicate-detection and policy-violation warnings',
        ],
        'integrates_with': ['HR', 'Payroll', 'Accounting', 'Sales', 'Project'],
        'metrics': [
            ('−85%', 'time from receipt to reimbursement'),
            ('<24h', 'average approval cycle'),
            ('100%', 'receipts OCR-extracted without manual entry'),
        ],
    },
}


def get_module_details(code: str) -> dict:
    """Return the structured detail payload for a module code, with empty defaults."""
    return MODULE_DETAILS.get(code, {
        'tagline': '',
        'highlights': [],
        'integrates_with': [],
        'metrics': [],
    })
