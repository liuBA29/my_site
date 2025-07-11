


from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.contrib.sitemaps.views import sitemap
from main_app.sitemaps import StaticViewSitemap


sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),  # подключаем sitemap.xml
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
