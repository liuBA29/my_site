## main_app/sitemaps.py
import datetime

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project, UsefulSoftware

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return ['main_app:home', 'main_app:my_projects', 'main_app:useful_soft', 'main_app:contact']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return datetime.date(2025, 7, 18) # вручную дата обновления страниц

class ProjectSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return reverse('main_app:project_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at


class UsefulSoftwareSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return UsefulSoftware.objects.all()

    def location(self, obj):
        return reverse('main_app:useful_soft_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at

