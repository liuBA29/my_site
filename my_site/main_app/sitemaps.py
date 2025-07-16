## main_app/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'
    domain = 'https://liuba.web.cloudcenter.ovh'

    def items(self):
        return ['main_app:home', 'main_app:my_projects', 'main_app:useful_soft', 'main_app:contact']

    def location(self, item):
         # получаем относительный путь, например '/my-projects/'
        return reverse(item)
