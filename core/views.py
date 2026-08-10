from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView

from .forms import ContactForm
from .models import Service, ERPModule
from blog.models import Post
from portfolio.models import CaseStudy, SuccessProject, Client, Certification


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modules'] = ERPModule.objects.filter(is_published=True, is_featured=True)
        ctx['services'] = Service.objects.filter(is_active=True)[:6]
        ctx['featured_case_studies'] = CaseStudy.objects.filter(is_published=True, is_featured=True)[:3]
        ctx['featured_projects'] = SuccessProject.objects.filter(is_published=True, is_featured=True)[:3]
        ctx['featured_clients'] = Client.objects.filter(is_featured=True)
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