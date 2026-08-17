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
from .pdf import render_quote_pdf
from blog.models import Post
from portfolio.models import CaseStudy, SuccessProject, Client, Certification


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modules'] = ERPModule.objects.filter(is_published=True, is_featured=True)
        ctx['services'] = Service.objects.filter(is_active=True)[:11]
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