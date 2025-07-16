
# my_site.urls.py

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

from main_app.views import robots_txt
from main_app.sitemaps import StaticViewSitemap, ProjectSitemap, UsefulSoftwareSitemap


from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.http import HttpResponse


# def sitemap_with_encoding(request, sitemaps, **kwargs):
#     response = django_sitemap(request, sitemaps, **kwargs)
#     # Если это TemplateResponse, нужно сначала отрендерить
#     if hasattr(response, 'render') and callable(response.render):
#         response.render()
#     xml_prolog = b'<?xml version="1.0" encoding="UTF-8"?>\n'
#     content = response.content
#     if not content.startswith(xml_prolog):
#         content = xml_prolog + content
#     return HttpResponse(content, content_type='application/xml; charset=utf-8')


sitemaps = {
    'static': StaticViewSitemap,
    'projects': ProjectSitemap,
    'useful_soft': UsefulSoftwareSitemap,
}




urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', django_sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
] + i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("i18n/", include("django.conf.urls.i18n")),
    path('', include('main_app.urls', namespace='main_app')),
    path('notes/', include('notes_app.urls', namespace='notes')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('chat/', include('chat.urls', namespace='chat')),
    prefix_default_language=False,
)





if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
