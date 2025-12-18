# main_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm






def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Sitemap: https://liuba.site/sitemap.xml",
        "Sitemap: https://liuba.site/mysitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


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



def free_soft(request):
    soft = FreeSoftware.objects.all()
    context = {'soft': soft}

    return render(request, 'main_app/free_soft.html', context)

def free_soft_detail(request, slug):
    soft = get_object_or_404(FreeSoftware, slug=slug)
    context = {'soft': soft}

    return render(request, 'main_app/free_soft_detail.html', context)

def business_soft(request):
    soft = BusinessSoftware.objects.all()
    context = {'soft': soft}

    return render(request, 'main_app/business_soft.html', context)

def business_soft_detail(request, slug):
    soft = get_object_or_404(BusinessSoftware, slug=slug)
    context = {'soft': soft}

    return render(request, 'main_app/business_soft_detail.html', context)

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


def order_request(request):
    """Страница с формой заказа"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        # Передаем request в форму для получения IP адреса (для проверки Turnstile)
        form.request = request
        if form.is_valid():
            order = form.save()  # Сохраняем заказ в базу данных
            messages.success(
                request, 
                f'Спасибо, {order.client_name}! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('main_app:order_request')  # Перенаправляем на ту же страницу с сообщением
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = OrderForm()
    
    return render(request, 'main_app/order_request.html', {
        'form': form,
        'CLOUDFLARE_TURNSTILE_SITE_KEY': settings.CLOUDFLARE_TURNSTILE_SITE_KEY
    })

