
# my_site.urls.py

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

from main_app.views import robots_txt
from main_app.sitemaps import StaticViewSitemap, ProjectSitemap, UsefulSoftwareSitemap
from django.contrib.sitemaps.views import sitemap

from django.http import HttpResponse




sitemaps = {
    'static': StaticViewSitemap,
    'projects': ProjectSitemap,
    'useful_soft': UsefulSoftwareSitemap,
}

def sitemap_view(request):
    response = sitemap(request, sitemaps)
    response["X-Robots-Tag"] = "index, follow"
    return response


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap_view, name='sitemap'),

    path('robots.txt', robots_txt, name='robots_txt'),
] + i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("i18n/", include("django.conf.urls.i18n")),
    path('', include('main_app.urls', namespace='main_app')),
    path('notes/', include('notes_app.urls', namespace='notes')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('agregator/', include('agregator.urls')),

    prefix_default_language=False,
)





if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
