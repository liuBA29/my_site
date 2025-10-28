# main_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.views import send_telegram_message
from django.utils.timezone import now
from django.contrib.sitemaps import Sitemap
from django.urls import reverse






def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Sitemap: https://liuba.web.cloudcenter.ovh/sitemap.xml",
        "Sitemap: https://liuba.web.cloudcenter.ovh/mysitemap.xml"
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


@csrf_exempt
def safari_exit_beacon(request):
    if request.method == 'POST':
        # Отправляем уведомление об уходе только если ранее был зафиксирован заход
        if request.session.get('safari_enter_notified') and not request.session.get('safari_exit_notified'):
            current_dt = now().strftime('%Y-%m-%d %H:%M:%S %Z')
            try:
                send_telegram_message(
                    f"с сайта ВЫШЛИ (Safari) в такое-то время: {current_dt}"
                )
                request.session['safari_exit_notified'] = True
            except Exception:
                pass
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=405)

@csrf_exempt
def safari_css_status(request):
    if request.method == 'POST':
        status = request.POST.get('status')  # 'ok' | 'error'
        href = request.POST.get('href') or ''
        detail = request.POST.get('detail') or ''
        try:
            send_telegram_message(
                f"Safari CSS статус: {status}; href: {href}; detail: {detail}"
            )
        except Exception:
            pass
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=405)

