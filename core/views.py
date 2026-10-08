from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView, FormView
from datetime import datetime as dt_cls, timedelta

from .forms import ContactForm
from .models import (
    Service, ERPModule, PricingConfig, QuoteLead,
    Appointment, AvailabilityRule, BlockedDate,
    SiteSettings, get_available_slots,
)
from .module_data import get_module_icon, get_module_details
from . import booking_emails


# End-to-end workflow shown on the home page for each service.
# ``workflows`` is built from the two sources below: the step names and the
# per-service icon keys. The result is a list of (step_label, icon_svg) tuples
# so the template can render each step with its matching icon in one pass.
SERVICE_WORKFLOWS = {
    "small-erp-implementation":              ["Discover", "Configure", "Import Data", "Train Team", "Go-Live"],
    "odoo-community-erp-implementation":     ["Provision Server", "Install Modules", "Custom Dev", "Deploy", "Monitor"],
    "data-migration":                        ["Audit Source", "Map Fields", "Clean & Validate", "Test Run", "Cutover"],
    "version-migration":                     ["Audit Code", "Adapt APIs", "Migrate DB", "Regression Test", "Release"],
    "custom-feature-development":            ["Requirements", "Architecture", "Build", "Test", "Deploy"],
    "functional-consultancy":                ["Discovery", "Map Processes", "Gap Analysis", "Roadmap", "Handover"],
    "run-odoo-server":                       ["Provision", "Automated Backup", "Monitor", "Patch", "Support"],
    "deployment":                            ["Containerize", "CI/CD", "Staging", "Production", "Rollback"],
    "odoo-server-optimization":              ["Profile", "Tune Workers", "Tune DB", "Caching", "Benchmark"],
    "bug-fix-in-existing-software":          ["Reproduce", "Root Cause", "Fix", "Test", "Postmortem"],
    "performance-enhancement":               ["Measure", "Find Hotspots", "Optimize", "Verify", "Monitor"],
}


# Each service gets a unique icon + accent color so the tabbed board reads
# visually at a glance. ``accent_key`` maps to a CSS class on the template
# (see ``svc-accent-*`` in custom.css).
SERVICE_THEMES = {
    "small-erp-implementation": {
        "accent_key": "indigo",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>""",
    },
    "odoo-community-erp-implementation": {
        "accent_key": "purple",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4v6c0 4.5-3.5 7.5-8 8-4.5-.5-8-3.5-8-8V7l8-4z"/><path d="M9 12l2 2 4-4"/></svg>""",
    },
    "data-migration": {
        "accent_key": "cyan",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h13"/><path d="m11 3 4 4-4 4"/><path d="M21 17H8"/><path d="m13 21-4-4 4-4"/></svg>""",
    },
    "version-migration": {
        "accent_key": "amber",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/></svg>""",
    },
    "custom-feature-development": {
        "accent_key": "pink",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m8 6-5 6 5 6"/><path d="m16 6 5 6-5 6"/><path d="m14 4-4 16"/></svg>""",
    },
    "functional-consultancy": {
        "accent_key": "yellow",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.8.7 1 1.4 1 2.3v1h6v-1c0-.9.2-1.6 1-2.3A7 7 0 0 0 12 2z"/></svg>""",
    },
    "run-odoo-server": {
        "accent_key": "green",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="6" rx="1.5"/><rect x="3" y="14" width="18" height="6" rx="1.5"/><path d="M7 7h.01M7 17h.01"/></svg>""",
    },
    "deployment": {
        "accent_key": "orange",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>""",
    },
    "odoo-server-optimization": {
        "accent_key": "blue",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>""",
    },
    "bug-fix-in-existing-software": {
        "accent_key": "red",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>""",
    },
    "performance-enhancement": {
        "accent_key": "teal",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-5"/></svg>""",
    },
}


# Reusable icon library for workflow steps. Each value is a 24x24 inline SVG
# stroke-only icon (matches the rest of the site). The icons inherit color
# via currentColor so the per-service accent bleeds through.
STEP_ICONS = {
    "search":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    "clipboard":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="2" width="8" height="4" rx="1.5"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6M9 16h4"/></svg>',
    "grid":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
    "filter":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5h18l-7 8v6l-4-2v-4z"/></svg>',
    "check":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l4 4L19 7"/></svg>',
    "play":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 5l12 7-12 7z"/></svg>',
    "swap":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h13l-4-4"/><path d="M21 16H8l4 4"/></svg>',
    "rocket":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>',
    "code":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m8 6-5 6 5 6"/><path d="m16 6 5 6-5 6"/><path d="m14 4-4 16"/></svg>',
    "wrench":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 1 5.66 5.66l-1.42 1.42a4 4 0 0 1-5.66-5.66l-6.91 6.91a2.12 2.12 0 1 0 3 3l5.66-5.66"/></svg>',
    "database":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v6c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 11v6c0 1.66 4 3 9 3s9-1.34 9-3v-6"/></svg>',
    "chart":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-5"/></svg>',
    "gauge":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 14l4-4"/><path d="M3 14a9 9 0 1 1 18 0"/></svg>',
    "lightning":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>',
    "eye":         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    "users":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "support":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><circle cx="12" cy="17" r="0.5" fill="currentColor"/></svg>',
    "save":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8M7 3v5h8"/></svg>',
    "activity":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h4l3-9 4 18 3-9h4"/></svg>',
    "fire":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2c4 4 6 7 6 10a6 6 0 0 1-12 0c0-2 1-3 2-4 0 1 1 2 2 2 0-3-1-5 2-8z"/></svg>',
    "container":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
    "workflow":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="15" width="6" height="6" rx="1"/><path d="M9 6h6a3 3 0 0 1 3 3v6"/></svg>',
    "server":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="6" rx="1.5"/><rect x="3" y="14" width="18" height="6" rx="1.5"/><circle cx="7" cy="7" r="0.5" fill="currentColor"/><circle cx="7" cy="17" r="0.5" fill="currentColor"/></svg>',
    "package":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16.5 9.4 7.55 4.24"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="m3.27 6.96 8.73 5.05 8.73-5.05"/><path d="M12 22.08V12"/></svg>',
    "sliders":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/></svg>',
    "undo":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-15-6.7L3 13"/></svg>',
    "blueprint":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 8h10M7 12h10M7 16h6"/></svg>',
    "handshake":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 5"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/></svg>',
    "lightbulb":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.8.7 1 1.4 1 2.3v1h6v-1c0-.9.2-1.6 1-2.3A7 7 0 0 0 12 2z"/></svg>',
    "upload":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>',
    "bug":         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2 5 5"/><path d="m19 5-3-3"/><path d="M10 8h4"/><path d="M10 11h4"/><path d="M9 16a3 3 0 0 0 6 0v-5H9z"/><path d="M5 12H2M22 12h-3M5 18l-2 2M19 18l2 2M5 6 3 4M19 6l2-4"/></svg>',
    "doc":         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h4"/></svg>',
}


# Maps each service's 5 workflow steps to a relevant icon from STEP_ICONS.
SERVICE_STEP_ICONS = {
    "small-erp-implementation":              ["search", "sliders", "upload", "users", "rocket"],
    "odoo-community-erp-implementation":     ["server", "package", "code", "rocket", "activity"],
    "data-migration":                        ["search", "grid", "filter", "play", "swap"],
    "version-migration":                     ["search", "code", "database", "check", "rocket"],
    "custom-feature-development":            ["clipboard", "blueprint", "code", "check", "rocket"],
    "functional-consultancy":                ["search", "workflow", "chart", "grid", "handshake"],
    "run-odoo-server":                       ["server", "save", "activity", "wrench", "support"],
    "deployment":                            ["container", "workflow", "server", "rocket", "undo"],
    "odoo-server-optimization":              ["gauge", "sliders", "database", "lightning", "chart"],
    "bug-fix-in-existing-software":          ["bug", "search", "wrench", "check", "doc"],
    "performance-enhancement":               ["gauge", "fire", "lightning", "chart", "eye"],
}


def _build_workflows():
    """service_slug -> [(step_label, icon_svg), ...] for the 5 workflow steps."""
    out = {}
    for slug, steps in SERVICE_WORKFLOWS.items():
        keys = SERVICE_STEP_ICONS.get(slug, [])
        icons = [STEP_ICONS.get(k, "") for k in keys]
        out[slug] = list(zip(steps, icons))
    return out


SERVICE_WORKFLOWS_VISUAL = _build_workflows()
from .pdf import render_quote_pdf
from blog.models import Post
from portfolio.models import CaseStudy, SuccessProject, Client, Certification


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modules'] = ERPModule.objects.filter(is_published=True, is_featured=True)
        ctx['services'] = Service.objects.filter(is_active=True)[:11]
        ctx['service_workflows'] = SERVICE_WORKFLOWS_VISUAL
        ctx['service_themes'] = SERVICE_THEMES
        ctx['pricing_tiers'] = PricingConfig.get_solo().catalog.get('tiers', [])
        ctx['featured_case_studies'] = CaseStudy.objects.filter(is_published=True, is_featured=True)[:3]
        ctx['featured_projects'] = SuccessProject.objects.filter(is_published=True, is_featured=True)[:3]
        ctx['featured_clients'] = Client.objects.filter(is_featured=True)
        ctx['testimonials'] = Client.objects.exclude(testimonial__isnull=True).exclude(testimonial__exact='')[:6]
        ctx['latest_posts'] = Post.objects.filter(is_published=True)[:3]
        # Real client list (ordered: Project Manager → Developer → Other) for the trusted-by marquee
        ctx['marquee_clients'] = CLIENTS
        return ctx
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['certifications'] = Certification.objects.all()[:6]
        return ctx


# Curated list of companies / projects I've undertaken, ordered by role
# (Project Manager first), then size of engagement, then alphabetical.
# Sourced from /media/project_taken.txt and /media/project_taken_comp_logo/.
CLIENTS = [
    {
        "name": "Smart Distribution (Pvt.) Ltd.",
        "url": "https://smartdistributionbd.com",
        "logo": "/static/images/clients/SDPL.png",
        "industry": "Import & Distribution",
        "role": "Project Manager, Technical Lead",
        "profile": "Smart Distribution (Pvt.) Ltd. is a rapidly growing one of the leading enterprises with business in import of quality consumer goods in Bangladesh.",
        "scope": "Medium ERP — Sales, Inventory (multi-warehouse, multi-company, multi-branch, multi-business unit), Foreign Purchase, LC Management.",
    },
    {
        "name": "SMS Corporation Ltd.",
        "url": "https://smserp.uslbd.com/",
        "logo": "/static/images/clients/sms.png",
        "industry": "Hardware Distribution",
        "role": "Project Manager, Technical Lead",
        "profile": "SMS Corporation Ltd. — hardware distribution in Uttara, Dhaka, operating since 2001.",
        "scope": "Small ERP — Sales, Accounting, Inventory.",
    },
    {
        "name": "Smart Technologies (BD) Ltd.",
        "url": "https://smartbd.com",
        "logo": "/static/images/clients/smart.png",
        "industry": "ICT Distribution (100+ global brands)",
        "role": "Developer, Maintainer",
        "profile": "Smart Technologies (BD) Ltd. is one of the largest and most trusted ICT distribution companies in Bangladesh. Established in 1998, the company distributes, integrates, and delivers IT products, consumer electronics, networking, security, and enterprise solutions nationwide. Authorised distributor of 100+ global brands including Microsoft, Intel, Google, Apple, Samsung, HP, Dell, Lenovo, Sony, Acer, HPE, Fortinet, Kaspersky, Oracle, Logitech, Hikvision and Dahua.",
        "scope": "Large ERP — Foreign Purchase, LC Management, Sales, Inventory (multi-warehouse, multi-company, multi-branch, multi-business unit), HR, HR APP API, External Portals, External APIs.",
    },
    {
        "name": "Smart Printing Solution Ltd. (SPSL)",
        "url": "https://spslbd.com",
        "logo": "/static/images/clients/spsl_logo.webp",
        "industry": "Printing Solutions · 9 branches",
        "role": "Developer, Maintainer",
        "profile": "Smart Printing Solution Ltd. (SPSL) is Bangladesh's leading authorised printing technology solutions provider — 12 world-leading brands, 9 branches nationwide, trusted by over 1,000 organisations.",
        "scope": "Medium ERP — Foreign Purchase, LC Management, Sales, Inventory (multi-warehouse, multi-company, multi-branch, multi-business unit), HR, HR APP API, External Portals, External APIs.",
    },
    {
        "name": "Global Office Automation Limited",
        "url": "https://globaloffice.com.bd/",
        "logo": "/static/images/clients/Global.png",
        "industry": "Stationery & Office Supplies",
        "role": "Developer, Maintainer",
        "profile": "GOAL is dedicated to delivering premium stationery and office supplies across Bangladesh, offering exceptional quality at reasonable prices. Brands include FABER-CASTELL, CASIO, Mitsubishi Pencil Co. (Uni-ball), Pentonic, and Staedtler.",
        "scope": "Medium ERP — Foreign Purchase, LC Management, Sales, Inventory (multi-warehouse, multi-company, multi-branch, multi-business unit), HR, HR APP API, External Portals, External APIs.",
    },
    {
        "name": "1000FIX Services",
        "url": "https://1000fix.com",
        "logo": "/static/images/clients/1000fix.png",
        "industry": "IT Service Network · 50+ centres · 300+ corporate clients",
        "role": "Developer, Maintainer",
        "profile": "Founded in 2017, 1000FiX Services Limited is one of Bangladesh's leading IT service providers, operating as a distinguished service arm of Smart Technologies (BD) Ltd. 50+ service centres nationwide, 400+ engineers, 600,000+ units serviced annually. Authorised service partner for 45+ global brands (HP, Dell, Lenovo, Samsung, Acer, Toshiba, Xiaomi). ISO 9001:2015 certified, 97% first-time fix rate.",
        "scope": "Medium ERP — Service Management, QC Management, Foreign Purchase, LC Management, Sales, Inventory (multi-warehouse, multi-company, multi-branch, multi-business unit), HR, HR APP API, External Portals, External APIs.",
    },
    {
        "name": "Digital Equipment Limited",
        "url": "https://digitalequipment.com.bd",
        "logo": "/static/images/clients/digital.png",
        "industry": "ICT Solutions & Distribution",
        "role": "Developer, Maintainer",
        "profile": "Digital Equipment Limited is one of the largest ICT solution and service companies in Bangladesh — a New Generation Turnkey IT Infrastructure Distribution, Solutions & Services Provider focused on Data Storage & Backup, Security Surveillance, Networking, and IT Security. Operating since 2001.",
        "scope": "Medium ERP — Sales, Inventory (multi-warehouse, multi-company, multi-branch, multi-business unit), HR, HR APP API, External Portals, External APIs.",
    },
    {
        "name": "Smart Safety & Automations Ltd.",
        "url": "https://smartsafety.com.bd",
        "logo": "/static/images/clients/Smart-Safety-Automations-Ltd-logo.png",
        "industry": "Safety, Security & Automation",
        "role": "Developer, Maintainer",
        "profile": "Smart Safety & Automations Ltd., a sister concern of Smart Technologies (BD) Ltd., is a premier provider of advanced safety, security, and automation solutions — fire alarm systems, CCTV surveillance, access control, building management systems, and other state-of-the-art automation technologies.",
        "scope": "Medium ERP — Sales, Inventory (multi-warehouse, multi-company, multi-branch), HR, HR APP API, External Portals, External APIs, Purchase Requisition.",
    },
    {
        "name": "Bangladesh Police — Highway Police",
        "url": "https://www.police.gov.bd",
        "logo": "/static/images/clients/high_way_police.jpeg",
        "industry": "Government",
        "role": "Developer",
        "profile": "Bangladesh Police — Highway Police division. A confidential government engagement.",
        "scope": "Confidential development work for the Highway Police division under Bangladesh Police — built as a Developer. Specifics under NDA.",
    },
    {
        "name": "Link3 Technologies Ltd.",
        "url": "https://www.link3.net",
        "logo": "/static/images/clients/link3.png",
        "industry": "ISP & Telecom",
        "role": "Developer",
        "profile": "Link3 Technologies Ltd. — ISP and telecom operator in Bangladesh. Known for fibre-to-the-home connectivity and enterprise services.",
        "scope": "Built an AI-powered network issue resolver for Link3 — browser-automation AI that handles customer network troubleshooting end-to-end.",
    },
    {
        "name": "Litmond Shipping Ltd.",
        "url": "",
        "logo": "/static/images/clients/litmond.jpeg",
        "industry": "Shipping",
        "role": "Developer",
        "profile": "Litmond Shipping Ltd. — shipping company operating in Bangladesh.",
        "scope": "Built Litmond Shipping's business website — public-facing web presence for their shipping services.",
    },
]
# Sourced from https://apps.odoo.com/apps/modules/browse?author=Mostakim%20Jihad
APP_STORE_MODULES = [
    {
        "slug": "hr_performance_kpi",
        "name": "KPI Management",
        "version": "19.0.1.0.1",
        "category": "Human Resources",
        "subcategory": "Performance",
        "tagline": "Define, assign and track KPI metrics with RAG scoring and dashboards.",
        "summary": "A complete KPI management module — define metrics, assign them to employees or departments, track periodic results with an approval workflow, and monitor performance on a real-time dashboard.",
        "features": [
            "Hierarchical KPI categories with parent/child trees",
            "Quantitative or qualitative KPI templates with RAG thresholds",
            "Three calculation methods: Manual Entry, ORM Query, Formula",
            "Assignments to employee or department with state machine",
            "Draft → Submitted → Reviewed → Approved workflow",
            "Real-time dashboard with summary cards and RAG distribution",
            "Pivot and graph views for cross-tab analysis",
            "Multi-company ready with record rules",
        ],
        "depends": ["hr", "mail"],
        "license": "LGPL-3",
        "price": "Free",
        "downloads": 21,
        "store_url": "https://apps.odoo.com/apps/modules/19.0/hr_performance_kpi",
        "icon_url": "/static/images/store/hr_performance_kpi.png",
    },
    {
        "slug": "salon_booking_pro",
        "name": "Salon Management",
        "version": "19.0.1.0.0",
        "category": "Human Resources",
        "subcategory": "Salon",
        "tagline": "Modern salon & spa booking portal with multi-branch support.",
        "summary": "A complete salon & spa management module with a modern customer-facing booking portal — branches, stylists, services, appointments, and a multi-step booking wizard for guests.",
        "features": [
            "Multiple branches with opening hours, manager and team",
            "Service catalog with categories, duration, price and per-branch availability",
            "Stylists with services, weekly schedule and public bio",
            "Full booking lifecycle: draft → confirmed → in progress → done",
            "Customer-facing booking portal with hero and category browse",
            "Multi-step booking wizard with live availability check",
            "Guest booking with optional signup after confirmation",
            "Customer appointment history and cancellation via token link",
            "Pivot and graph analytics by branch, service, stylist, status",
        ],
        "depends": ["auth_signup", "hr", "mail", "portal"],
        "license": "LGPL-3",
        "price": "Free",
        "downloads": 13,
        "store_url": "https://apps.odoo.com/apps/modules/19.0/salon_booking_pro",
        "icon_url": "/static/images/store/salon_booking_pro.png",
    },
    {
        "slug": "petty_cash_daily",
        "name": "Petty Cash Daily",
        "version": "19.0.1.0.0",
        "category": "Finance",
        "subcategory": "Accounting",
        "tagline": "Daily cash box management with a beautiful expense dashboard.",
        "summary": "A daily-first petty cash module — define cash boxes, record money in/out, open and close daily sessions, and watch a real-time expense dashboard that an office manager can open every morning.",
        "features": [
            "Cash boxes with custodian, opening balance and currency",
            "Money in / money out transactions with receipt attachments",
            "Configurable per-fund approval limit auto-routes expenses",
            "Daily session with expected vs actual balance and variance alert",
            "Replenishment requests with full approval workflow",
            "Daily expense dashboard: income, expenses, net change, balance",
            "Seven-day cash-flow trend and top categories for the month",
            "Funds kanban with color-coded custodian and category budgets",
            "Chatter on every stateful model with Draft → Paid transitions",
            "Integration with account, hr and mail modules",
        ],
        "depends": ["account", "hr", "mail"],
        "license": "LGPL-3",
        "price": "Free",
        "downloads": 6,
        "store_url": "https://apps.odoo.com/apps/modules/19.0/petty_cash_daily",
        "icon_url": "/static/images/store/petty_cash_daily.png",
    },
]


class StoreView(TemplateView):
    """Public catalogue of free Odoo App Store modules authored by Mostakim Jihad."""

    template_name = "core/store.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["store_modules"] = APP_STORE_MODULES
        ctx["total_downloads"] = sum(m["downloads"] for m in APP_STORE_MODULES)
        return ctx


class ProjectsView(TemplateView):
    """Projects I've undertaken across my career — ordered by role (Project Manager first)."""

    template_name = "core/projects.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["clients"] = CLIENTS
        # group by role for the section heads
        ctx["clients_by_role"] = {
            "manager": [c for c in CLIENTS if "Project Manager" in c["role"]],
            "developer": [c for c in CLIENTS if "Project Manager" not in c["role"] and ("Developer" in c["role"] or "Maintainer" in c["role"])],
            "other": [c for c in CLIENTS if "Project Manager" not in c["role"] and "Developer" not in c["role"] and "Maintainer" not in c["role"]],
        }
        return ctx


class ClientListView(TemplateView):
    """Lightweight client logos grid backed by the same CLIENTS dict."""

    template_name = "portfolio/clients.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["clients"] = CLIENTS
        ctx["clients_with_testimonials"] = [c for c in CLIENTS if c.get("testimonial")]
        return ctx


class ServiceListView(ListView):
    model = Service
    template_name = 'core/services.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['service_workflows'] = SERVICE_WORKFLOWS_VISUAL
        ctx['service_themes'] = SERVICE_THEMES
        return ctx


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'core/service_detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


class ModuleListView(ListView):
    model = ERPModule
    template_name = 'core/modules.html'
    context_object_name = 'modules'

    def get_queryset(self):
        return ERPModule.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['module_icons'] = {m.demo_code: get_module_icon(m.demo_code) for m in ctx['modules']}
        ctx['media_url'] = settings.MEDIA_URL
        return ctx


class ModuleDetailView(DetailView):
    model = ERPModule
    template_name = 'core/module_detail.html'
    context_object_name = 'module'

    def get_queryset(self):
        return ERPModule.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Group other modules for the "more modules" footer
        others = list(ERPModule.objects.filter(is_published=True).exclude(pk=self.object.pk)[:6])
        ctx['other_modules'] = others
        ctx['module_icon'] = get_module_icon(self.object.demo_code)
        ctx['module_details'] = get_module_details(self.object.demo_code)
        ctx['other_module_icons'] = {m.demo_code: get_module_icon(m.demo_code) for m in others}
        ctx['media_url'] = settings.MEDIA_URL
        return ctx


# ---------- Products (ERP modules grouped by business function) ----------

# Business-function categories that buyers actually search for. Each
# category maps to the slugs of ERPModule rows that satisfy it; a single
# module can live in multiple categories (e.g. Point of Sale is both
# Commerce and Operations).
PRODUCT_CATEGORIES = [
    {
        "key": "hrm",
        "label": "HRM Systems",
        "tagline": "People, payroll, attendance — your team, on one record.",
        "description": "Run payroll, attendance, leaves, and contracts on a single employee record that HR, managers, and finance all share.",
        "theme": "pink",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
        "module_slugs": ["human-resources", "expenses-approvals", "subscriptions"],
    },
    {
        "key": "crm",
        "label": "CRM & Sales",
        "tagline": "Quote-to-cash in one pipeline — leads, deals, renewals, support.",
        "description": "Every lead, quote, and renewal in one pipeline with stage automation, forecasting, and a helpdesk that closes the loop.",
        "theme": "purple",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="m22 11-3 3-2-2"/></svg>""",
        "module_slugs": ["sales", "crm", "subscriptions", "helpdesk"],
    },
    {
        "key": "scm",
        "label": "Supply Chain & Operations",
        "tagline": "From supplier to shop floor to customer — stock you can trust.",
        "description": "Multi-warehouse inventory, barcoded picking, dropship routes, and routing-aware manufacturing — stock that always matches the books.",
        "theme": "orange",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/><path d="M3 9V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4"/><path d="M9 22V12h6v10"/></svg>""",
        "module_slugs": ["inventory", "purchase", "manufacturing", "quality-maintenance", "field-service"],
    },
    {
        "key": "finance",
        "label": "Finance & Accounting",
        "tagline": "Books that close themselves — multi-entity, multi-currency, audit-ready.",
        "description": "Multi-entity ledgers, inter-company invoicing, automatic FX revaluation, and consolidated reporting — books an auditor can sign off on.",
        "theme": "green",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 9h20M9 21V9"/></svg>""",
        "module_slugs": ["accounting", "expenses-approvals"],
    },
    {
        "key": "commerce",
        "label": "Digital Commerce",
        "tagline": "Sell anywhere — counter, online, marketplace — one inventory, one truth.",
        "description": "POS, storefront, marketplaces, and fulfilment on a single inventory. Sell across every channel without overselling.",
        "theme": "blue",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>""",
        "module_slugs": ["point-of-sale", "ecommerce", "website", "marketing-automation"],
    },
    {
        "key": "productivity",
        "label": "Projects & Productivity",
        "tagline": "Bill by the hour, not the guess — timesheets, projects, support.",
        "description": "Timesheets, project billing, retainer contracts, and field-service scheduling — billable work tracked from start to invoice.",
        "theme": "yellow",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>""",
        "module_slugs": ["project", "field-service", "helpdesk"],
    },
]


class ProductListView(TemplateView):
    """Catalogue of ERP modules grouped by business function category."""

    template_name = "core/products.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        modules_by_slug = {m.slug: m for m in ERPModule.objects.filter(is_published=True)}
        # Build per-category groups, resolving module slugs to live records.
        # De-duplicate modules that appear in multiple categories.
        ctx["product_categories"] = []
        for cat in PRODUCT_CATEGORIES:
            modules = [modules_by_slug[s] for s in cat["module_slugs"] if s in modules_by_slug]
            ctx["product_categories"].append({**cat, "modules": modules})
        ctx["total_products"] = len(modules_by_slug)
        return ctx


class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/contact/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['services'] = Service.objects.filter(is_active=True)
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks! Your message has been sent. I'll get back to you within 24 hours.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below and try again.")
        return super().form_invalid(form)


class PricingView(TemplateView):
    """Dedicated pricing page with the live cost calculator."""
    template_name = 'core/pricing.html'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cfg = PricingConfig.get_solo()
        ctx['pricing'] = cfg
        ctx['tiers'] = cfg.catalog.get('tiers', [])
        ctx['addons'] = cfg.catalog.get('addons', [])
        ctx['discounts'] = cfg.catalog.get('discounts', [])
        return ctx


@require_POST
def quote_submit(request):
    """Save a QuoteLead and return the rendered PDF.

    Expects JSON body: { name, email, phone?, company?, notes?,
                         tier_id, currency, items: [{id,name,unit,unit_price_usd,qty,line_total_usd}, ...],
                         subtotal_usd, discount_percent, discount_usd, total_usd, usd_to_bdt }
    """
    import json
    from decimal import Decimal

    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    # Required
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    if not name or not email:
        return JsonResponse({'error': 'Name and email are required.'}, status=400)

    try:
        # 1. Save the lead first so it gets a primary key (used as the quote #)
        lead = QuoteLead(
            name=name[:120],
            email=email,
            phone=(data.get('phone') or '')[:40],
            company=(data.get('company') or '')[:160],
            notes=(data.get('notes') or ''),
            tier_id=(data.get('tier_id') or '')[:40],
            items=data.get('items') or [],
            subtotal_usd=Decimal(str(data.get('subtotal_usd', 0))),
            discount_percent=int(data.get('discount_percent', 0) or 0),
            discount_usd=Decimal(str(data.get('discount_usd', 0))),
            total_usd=Decimal(str(data.get('total_usd', 0))),
            currency=(data.get('currency') or 'USD')[:3],
            usd_to_bdt=Decimal(str(data.get('usd_to_bdt', 110))),
            ip=request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:400],
        )
        lead.save()
        # 2. Render the PDF now that we have a quote number
        pdf_bytes = render_quote_pdf(lead)
        filename = f"quote-{name.lower().replace(' ', '-')[:40]}.pdf"
        lead.pdf.save(filename, ContentFile(pdf_bytes), save=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Could not save lead: {e}'}, status=500)

    # Stream the same PDF bytes back as a download
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['X-Quote-Lead-Id'] = str(lead.id)
    return response


# ---------------------------------------------------------------------------
# Booking / appointment API
# ---------------------------------------------------------------------------

def _client_ip(request):
    fwd = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    return fwd or request.META.get('REMOTE_ADDR') or None


@require_GET
def booking_calendar(request):
    """Return availability info for a given month so the picker can light up
    days that have any open slots.

    Query params: year (int), month (1-12). Returns:
        {
          "year": ..., "month": ...,
          "days": ["2026-08-30", ...]  // dates that have any open slot,
          "blocked": ["2026-09-04", ...],  // full-day BlockedDate entries
          "today": "2026-08-30",
        }
    """
    from datetime import date as date_cls

    today = timezone.localdate()
    try:
        year = int(request.GET.get('year') or today.year)
        month = int(request.GET.get('month') or today.month)
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Invalid year/month.')

    if month < 1 or month > 12:
        return HttpResponseBadRequest('Month must be 1-12.')

    advance = getattr(settings, 'BOOKING_ADVANCE_DAYS', 60)
    horizon = today + timedelta(days=advance)

    days_with_slots = []
    cursor = date_cls(year, month, 1)
    while cursor.month == month:
        if today <= cursor <= horizon:
            slots = get_available_slots(cursor, slot_minutes=getattr(settings, 'BOOKING_SLOT_MINUTES', 30))
            if slots:
                days_with_slots.append(cursor.isoformat())
        cursor += timedelta(days=1)

    blocked = list(
        BlockedDate.objects.filter(
            date__year=year, date__month=month, is_full_day=True,
        ).values_list('date', flat=True)
    )
    blocked = [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in blocked]

    return JsonResponse({
        'year': year,
        'month': month,
        'days': days_with_slots,
        'blocked': blocked,
        'today': today.isoformat(),
        'horizon': horizon.isoformat(),
    })


@require_GET
def booking_slots(request):
    """Return the open slot start-times for a single date.

    Query params: date=YYYY-MM-DD.

    Returns: {
        "date": "2026-08-30",
        "slot_minutes": 30,
        "slots": ["2026-08-30T10:00:00+06:00", ...]  // ISO in project TZ
    }
    """
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponseBadRequest('Missing date.')

    try:
        target = dt_cls.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseBadRequest('Invalid date format (YYYY-MM-DD).')

    today = timezone.localdate()
    advance = getattr(settings, 'BOOKING_ADVANCE_DAYS', 60)
    horizon = today + timedelta(days=advance)
    if target < today or target > horizon:
        return JsonResponse({'slots': [], 'date': date_str})

    slots = get_available_slots(target, slot_minutes=getattr(settings, 'BOOKING_SLOT_MINUTES', 30))
    return JsonResponse({
        'date': date_str,
        'slot_minutes': getattr(settings, 'BOOKING_SLOT_MINUTES', 30),
        'slots': [s.isoformat() for s in slots],
    })


@csrf_protect
@require_POST
def booking_create(request):
    """Create an Appointment from the modal form.

    Body (JSON): { name, email, phone?, company?, notes?,
                    start_iso, slot_minutes, timezone }
    """
    import json

    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    phone = (data.get('phone') or '').strip()
    company = (data.get('company') or '').strip()
    notes = (data.get('notes') or '').strip()
    start_iso = (data.get('start_iso') or '').strip()
    slot_minutes = int(data.get('slot_minutes') or getattr(settings, 'BOOKING_SLOT_MINUTES', 30))
    visitor_tz = (data.get('timezone') or '').strip() or 'Asia/Dhaka'

    # --- validate ---
    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if len(name) > 120:
        errors['name'] = 'Name is too long.'
    if not email:
        errors['email'] = 'Email is required.'
    elif '@' not in email or '.' not in email.split('@')[-1]:
        errors['email'] = 'Enter a valid email address.'
    if not start_iso:
        errors['start_iso'] = 'Please pick a time slot.'

    if errors:
        return JsonResponse({'errors': errors}, status=400)

    # --- parse start ---
    try:
        start_dt = dt_cls.fromisoformat(start_iso.replace('Z', '+00:00'))
        if timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt, timezone.utc)
        start_dt = start_dt.astimezone(timezone.get_current_timezone())
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid start time.'}, status=400)

    end_dt = start_dt + timedelta(minutes=slot_minutes)

    # --- race-condition guard: re-check availability at write time ---
    if Appointment.objects.filter(
        status='confirmed',
        start_datetime=start_dt,
    ).exists():
        return JsonResponse({
            'error': 'Sorry, that slot was just booked. Please pick another time.',
        }, status=409)

    if start_dt <= timezone.now():
        return JsonResponse({'error': 'Cannot book a slot in the past.'}, status=400)

    # --- save ---
    try:
        appt = Appointment.objects.create(
            name=name[:120],
            email=email,
            phone=phone[:40],
            company=company[:120],
            notes=notes,
            start_datetime=start_dt,
            end_datetime=end_dt,
            timezone=visitor_tz[:64],
            ip=_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:400],
        )
    except Exception as e:
        return JsonResponse({'error': f'Could not save booking: {e}'}, status=500)

    # --- emails ---
    booking_emails.send_confirmation_to_visitor(appt)
    booking_emails.send_notification_to_owner(appt)

    cancel_url = request.build_absolute_uri(
        reverse('booking_cancel', args=[appt.cancel_token])
    )
    confirm_url = request.build_absolute_uri(
        reverse('booking_confirmed', args=[appt.cancel_token])
    )

    return JsonResponse({
        'ok': True,
        'id': appt.id,
        'cancel_url': cancel_url,
        'confirm_url': confirm_url,
        'start_datetime': start_dt.isoformat(),
        'end_datetime': end_dt.isoformat(),
        'visitor_tz': visitor_tz,
    })


def booking_confirmed(request, token):
    """Public 'thanks, your call is booked' page reached via the modal."""
    try:
        appt = Appointment.objects.get(cancel_token=token)
    except Appointment.DoesNotExist:
        raise Http404('Booking not found.')

    return render(request, 'core/booking_confirmed.html', {
        'appointment': appt,
    })


def booking_cancel(request, token):
    """Public cancellation page — GET shows confirm, POST marks cancelled."""
    try:
        appt = Appointment.objects.get(cancel_token=token)
    except Appointment.DoesNotExist:
        raise Http404('Booking not found.')

    if request.method == 'POST':
        reason = (request.POST.get('reason') or '')[:2000]
        if appt.status != 'cancelled':
            appt.cancel(reason)
            booking_emails.send_cancellation_notice(appt)
        return render(request, 'core/booking_cancelled.html', {'appointment': appt})

    return render(request, 'core/booking_cancel.html', {'appointment': appt})