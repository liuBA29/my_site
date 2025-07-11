from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # Здесь укажи имена основных статичных страниц из urls.py твоего main_app
        return ['main_app:home', 'main_app:my_projects', 'main_app:useful_soft', 'main_app:contact']

    def location(self, item):
        return reverse(item)
