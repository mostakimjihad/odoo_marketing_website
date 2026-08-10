from django.urls import path

from . import views

app_name = 'portfolio'

# Portfolio URLs — included under /portfolio/ in core/urls.py.
# Clients and certifications live at /clients/ and /certifications/ (defined directly in core/urls.py).
urlpatterns = [
    path('', views.PortfolioView.as_view(), name='portfolio'),
    path('case-studies/<slug:slug>/', views.CaseStudyDetailView.as_view(), name='case_study_detail'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
]