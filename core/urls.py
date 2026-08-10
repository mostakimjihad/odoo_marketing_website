from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from portfolio.views import ClientListView, CertificationListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.app_urls')),
    path('portfolio/', include('portfolio.urls')),
    path('clients/', ClientListView.as_view(), name='clients'),
    path('certifications/', CertificationListView.as_view(), name='certifications'),
    path('blog/', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)