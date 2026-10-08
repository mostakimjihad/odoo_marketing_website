from django.urls import path
from django.http import HttpResponse

from . import views


def _mega_test(request):
    """Force mega menu open for visual inspection."""
    from django.template.loader import get_template
    base = get_template('base.html')
    extra_css = '<style>.mega-panel[data-mega-panel="explore"]{display:block!important;opacity:1!important;visibility:visible!important;transform:none!important}</style>'
    ctx = {'site_settings': None, 'request': request, 'mega_top_services': [], 'mega_featured_modules': []}
    html = base.render(ctx)
    html = html.replace('</head>', extra_css + '</head>')
    return HttpResponse(html)


urlpatterns = [
    path('mega-test/', _mega_test, name='mega_test'),
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServiceListView.as_view(), name='services'),
    path('services/<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('modules/', views.ModuleListView.as_view(), name='modules'),
    path('modules/<slug:slug>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('store/', views.StoreView.as_view(), name='store'),
    path('projects/', views.ProjectsView.as_view(), name='projects'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    path('pricing/quote/', views.quote_submit, name='quote_submit'),

    # Booking / appointment API + public pages
    path('booking/calendar/', views.booking_calendar, name='booking_calendar'),
    path('booking/slots/', views.booking_slots, name='booking_slots'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('booking/confirmed/<uuid:token>/', views.booking_confirmed, name='booking_confirmed'),
    path('booking/cancel/<uuid:token>/', views.booking_cancel, name='booking_cancel'),
]
