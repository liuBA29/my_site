## main_app/sitemaps.py
import datetime

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project, FreeSoftware, BusinessSoftware

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return ['main_app:home', 'main_app:cooperation', 'main_app:free_soft', 'main_app:business_soft', 'main_app:contact', 'main_app:requisites']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return datetime.date.today()  # Автоматически текущая дата

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


class FreeSoftwareSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return FreeSoftware.objects.all()

    def location(self, obj):
        return reverse('main_app:free_soft_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at


class BusinessSoftwareSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return BusinessSoftware.objects.all()

    def location(self, obj):
        return reverse('main_app:business_soft_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at

