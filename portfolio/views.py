from django.views.generic import ListView, DetailView

from .models import CaseStudy, SuccessProject, Client, Certification


class PortfolioView(ListView):
    """Combined portfolio page showing case studies + projects."""
    template_name = 'portfolio/portfolio.html'
    context_object_name = 'case_studies'

    def get_queryset(self):
        return CaseStudy.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['projects'] = SuccessProject.objects.filter(is_published=True)
        return ctx


class CaseStudyDetailView(DetailView):
    model = CaseStudy
    template_name = 'portfolio/case_study_detail.html'
    context_object_name = 'case_study'

    def get_queryset(self):
        return CaseStudy.objects.filter(is_published=True)


class ProjectDetailView(DetailView):
    model = SuccessProject
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return SuccessProject.objects.filter(is_published=True)


class ClientListView(ListView):
    model = Client
    template_name = 'portfolio/clients.html'
    context_object_name = 'clients'


class CertificationListView(ListView):
    model = Certification
    template_name = 'portfolio/certifications.html'
    context_object_name = 'certifications'