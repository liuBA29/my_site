# main_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

def simple_sitemap(request):
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://liuba.web.cloudcenter.ovh/</loc>
            <changefreq>monthly</changefreq>
            <priority>1.0</priority>
        </url>
        <url>
            <loc>https://liuba.web.cloudcenter.ovh/my-projects/</loc>
            <changefreq>monthly</changefreq>
            <priority>0.8</priority>
        </url>
        <url>
            <loc>https://liuba.web.cloudcenter.ovh/useful-soft/</loc>
            <changefreq>monthly</changefreq>
            <priority>0.8</priority>
        </url>
        <url>
            <loc>https://liuba.web.cloudcenter.ovh/contact/</loc>
            <changefreq>monthly</changefreq>
            <priority>0.8</priority>
        </url>
    </urlset>"""

    return HttpResponse(sitemap_xml, content_type="application/xml")





def page_view(request):
    page_path = request.path
    page_view = PageView.objects.filter(path=page_path).first()
    views = page_view.views_count if page_view else 0
    return render(request, 'main_app/page_view.html', {'views': views})




def main_page(request):
    project = Project.objects.all().values('title', 'description')
    show_alt_image = request.GET.get("alt") == "1"

    return render(request, 'main_app/index.html', )



def visits_log(request):
    logs = PageVisitLog.objects.order_by('-viewed_at')[:100]  # можно ограничить
    return render(request, 'main_app/visits_log.html', {'logs': logs})



def useful_soft(request):
    soft = UsefulSoftware.objects.all()
    context = {'soft': soft}

    return render(request, 'main_app/useful_soft.html', context)

def useful_soft_detail(request, slug):
    soft = get_object_or_404(UsefulSoftware, slug=slug)
    context = {'soft': soft}

    return render(request, 'main_app/useful_soft_detail.html', context)

def my_projects(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'main_app/my_projects.html', context)

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)

    context = {'project':project}
    return render(request, 'main_app/project_detail.html', context)



def contact(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/contact.html')

