from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServiceListView.as_view(), name='services'),
    path('services/<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('modules/', views.ModuleListView.as_view(), name='modules'),
    path('modules/<slug:slug>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    path('pricing/quote/', views.quote_submit, name='quote_submit'),
]