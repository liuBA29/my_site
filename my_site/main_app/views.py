# main_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from .forms import OrderForm
from accounts.views import send_telegram_message






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


def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_daily_order_limit(ip_address, max_orders_per_day=5):
    """Проверка лимита заявок с одного IP в день"""
    if not ip_address:
        return True, None  # Если IP нет, пропускаем проверку
    
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    orders_today = Order.objects.filter(
        ip_address=ip_address,
        created_at__gte=today_start
    ).count()
    
    if orders_today >= max_orders_per_day:
        return False, _("You can submit no more than %(max)d orders per day from one IP address. Please try again tomorrow.") % {'max': max_orders_per_day}
    
    return True, None


def order_request(request):
    """Страница с формой заказа"""
    if request.method == 'POST':
        # Проверяем лимит заявок с одного IP
        ip_address = get_client_ip(request)
        can_submit, limit_error = check_daily_order_limit(ip_address, max_orders_per_day=5)
        
        if not can_submit:
            messages.error(request, limit_error)
            form = OrderForm(request.POST)
        else:
            form = OrderForm(request.POST)
            # Передаем request в форму для получения IP адреса (для проверки Turnstile)
            form.request = request
            if form.is_valid():
                order = form.save(commit=False)  # Не сохраняем сразу
                order.ip_address = ip_address  # Сохраняем IP адрес
                order.save()  # Теперь сохраняем
                
                # Отправляем уведомление в Telegram
                telegram_message = (
                    f"🆕 Новая заявка!\n\n"
                    f"👤 Имя: {order.client_name}\n"
                    f"📧 Email: {order.client_email}\n"
                    f"📞 Телефон: {order.client_phone or 'не указан'}\n"
                    f"💼 Услуга: {order.service_type}\n"
                    f"📝 Описание: {order.description[:200]}{'...' if len(order.description) > 200 else ''}\n"
                    f"🌐 IP: {ip_address}\n"
                    f"🆔 ID заказа: {order.id}"
                )
                try:
                    send_telegram_message(telegram_message)
                except Exception as e:
                    print(f"Ошибка отправки в Telegram: {e}")
                
                messages.success(
                    request, 
                    _('Thank you, %(name)s! Your order has been received. We will contact you soon.') % {'name': order.client_name}
                )
                return redirect('main_app:order_request')  # Перенаправляем на ту же страницу с сообщением
            else:
                messages.error(request, _('Please correct the errors in the form.'))
    else:
        form = OrderForm()
    
    return render(request, 'main_app/order_request.html', {
        'form': form,
        'CLOUDFLARE_TURNSTILE_SITE_KEY': settings.CLOUDFLARE_TURNSTILE_SITE_KEY
    })

