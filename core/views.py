from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView, FormView

from .forms import ContactForm
from .models import Service, ERPModule, PricingConfig, QuoteLead


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
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['certifications'] = Certification.objects.all()[:6]
        return ctx


class ServiceListView(ListView):
    model = Service
    template_name = 'core/services.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


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


class ModuleDetailView(DetailView):
    model = ERPModule
    template_name = 'core/module_detail.html'
    context_object_name = 'module'

    def get_queryset(self):
        return ERPModule.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Group other modules for the "more modules" footer
        ctx['other_modules'] = ERPModule.objects.filter(is_published=True).exclude(pk=self.object.pk)[:6]
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
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
        "module_slugs": ["human-resources", "expenses-approvals", "subscriptions"],
    },
    {
        "key": "crm",
        "label": "CRM & Sales",
        "tagline": "Quote-to-cash in one pipeline — leads, deals, renewals, support.",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="m22 11-3 3-2-2"/></svg>""",
        "module_slugs": ["sales", "crm", "subscriptions", "helpdesk"],
    },
    {
        "key": "scm",
        "label": "Supply Chain & Operations",
        "tagline": "From supplier to shop floor to customer — stock you can trust.",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/><path d="M3 9V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4"/><path d="M9 22V12h6v10"/></svg>""",
        "module_slugs": ["inventory", "purchase", "manufacturing", "quality-maintenance", "field-service"],
    },
    {
        "key": "finance",
        "label": "Finance & Accounting",
        "tagline": "Books that close themselves — multi-entity, multi-currency, audit-ready.",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 9h20M9 21V9"/></svg>""",
        "module_slugs": ["accounting", "expenses-approvals"],
    },
    {
        "key": "commerce",
        "label": "Digital Commerce",
        "tagline": "Sell anywhere — counter, online, marketplace — one inventory, one truth.",
        "icon": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>""",
        "module_slugs": ["point-of-sale", "ecommerce", "website", "marketing-automation"],
    },
    {
        "key": "productivity",
        "label": "Projects & Productivity",
        "tagline": "Bill by the hour, not the guess — timesheets, projects, support.",
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