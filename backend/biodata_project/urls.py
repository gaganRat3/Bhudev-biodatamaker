from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from pathlib import Path
from .views import serve_static_html

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    path('admin/', admin.site.urls),
    path('api/', include('biodata.urls')),
    # Frontend pages served as static HTML (no Django template processing)
    path('', lambda request: serve_static_html(request, 'index.html'), name='home'),
    path('index.html', lambda request: serve_static_html(request, 'index.html')),
    path('login.html', lambda request: serve_static_html(request, 'login.html')),
    path('biodata-form.html', lambda request: serve_static_html(request, 'biodata-form.html')),
    path('template-page.html', lambda request: serve_static_html(request, 'template-page.html')),
    path('upgrade.html', lambda request: serve_static_html(request, 'upgrade.html')),
    path('biodata-list.html', lambda request: serve_static_html(request, 'biodata-list.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve frontend static assets at /css, /js, /assets so existing HTML paths work
    FRONTEND_ROOT = Path(settings.BASE_DIR).parent
    urlpatterns += static('/css/', document_root=FRONTEND_ROOT / 'css')
    urlpatterns += static('/js/', document_root=FRONTEND_ROOT / 'js')
    urlpatterns += static('/assets/', document_root=FRONTEND_ROOT / 'assets')
