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
        
        # Сохраняем информацию о продукте для отображения в форме при ошибке
        product_name = request.POST.get('product_name', '')
        product_version = request.POST.get('product_version', '')
        product_price = request.POST.get('product_price', '')
        product_info = {
            'product_name': product_name,
            'product_version': product_version,
            'product_price': product_price
        } if product_name else None
        
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
                # Сохраняем информацию о продукте из скрытых полей
                order.product_name = request.POST.get('product_name', '')
                order.product_version = request.POST.get('product_version', '')
                order.product_price = request.POST.get('product_price', '')
                order.save()  # Теперь сохраняем
                
                # Формируем сообщение для Telegram
                telegram_message = (
                    f"🆕 Новая заявка!\n\n"
                    f"👤 Имя: {order.client_name}\n"
                    f"📧 Email: {order.client_email}\n"
                    f"📞 Телефон: {order.client_phone or 'не указан'}\n"
                    f"💼 Услуга: {order.service_type}\n"
                )
                
                # Добавляем информацию о продукте, если она есть
                if order.product_name:
                    telegram_message += f"📦 Продукт: {order.product_name}\n"
                    if order.product_version:
                        telegram_message += f"🏷️ Версия: {order.product_version}\n"
                    if order.product_price:
                        telegram_message += f"💰 Цена: {order.product_price}\n"
                    telegram_message += "\n"
                
                telegram_message += (
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
        # Предзаполняем форму, если передан параметр service_type
        initial_data = {}
        service_type = request.GET.get('service_type', '')
        if service_type:
            # Проверяем, что значение валидно (существует в choices формы)
            valid_service_types = [
                'Website development',
                'Software development',
                'Project modification',
                'Technical support',
                'Consultation',
                'Other'
            ]
            if service_type in valid_service_types:
                initial_data['service_type'] = service_type
        
        form = OrderForm(initial=initial_data)
        
        # Получаем информацию о продукте из GET параметров
        product_name = request.GET.get('product_name', '')
        product_version = request.GET.get('product_version', '')
        product_price = request.GET.get('product_price', '')
        product_info = {
            'product_name': product_name,
            'product_version': product_version,
            'product_price': product_price
        } if product_name else None
    
    return render(request, 'main_app/order_request.html', {
        'form': form,
        'product_info': product_info,
        'CLOUDFLARE_TURNSTILE_SITE_KEY': settings.CLOUDFLARE_TURNSTILE_SITE_KEY
    })


def detect_os(user_agent):
    """Определяет операционную систему из User-Agent"""
    if not user_agent:
        return 'Unknown'
    
    user_agent_lower = user_agent.lower()
    
    # Проверяем Windows
    if 'windows' in user_agent_lower:
        return 'Windows'
    # Проверяем macOS
    elif 'mac' in user_agent_lower or 'darwin' in user_agent_lower:
        return 'macOS'
    # Проверяем Linux
    elif 'linux' in user_agent_lower:
        return 'Linux'
    # Проверяем Android
    elif 'android' in user_agent_lower:
        return 'Android'
    # Проверяем iOS
    elif 'iphone' in user_agent_lower or 'ipad' in user_agent_lower or 'ipod' in user_agent_lower:
        return 'iOS'
    else:
        return 'Unknown'


def track_download(request, file_type, slug=None, file_id=None):
    """
    Отслеживает скачивания файлов и отправляет уведомления в Telegram
    
    file_type: 'pdf_instruction', 'installer_ru', 'installer_en', 'demo_ru', 'demo_en'
    slug: slug объекта (для soft или project)
    file_id: ID объекта (альтернатива slug)
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    referer = request.META.get('HTTP_REFERER', 'Unknown')
    
    download_url = None
    file_name = None
    item_name = None
    
    try:
        # Определяем тип объекта и получаем его
        if slug:
            # Пробуем найти в FreeSoftware
            soft = FreeSoftware.objects.filter(slug=slug).first()
            if not soft:
                # Пробуем найти в BusinessSoftware
                soft = BusinessSoftware.objects.filter(slug=slug).first()
            
            if soft:
                item_name = soft.name
                if file_type == 'pdf_instruction' and soft.instruction_pdf:
                    download_url = soft.get_pdf_url()
                    file_name = "PDF инструкция"
                elif file_type == 'installer_ru' and soft.download_link:
                    download_url = soft.download_link
                    file_name = "Установщик (RU)"
                elif file_type == 'installer_en' and soft.english_link:
                    download_url = soft.english_link
                    file_name = "Установщик (EN)"
        
        # Если не нашли в soft, пробуем Project
        if not download_url and slug:
            project = Project.objects.filter(slug=slug).first()
            if project:
                item_name = project.title
                if file_type == 'demo_ru' and project.demo_link_ru:
                    download_url = project.demo_link_ru
                    file_name = "Демо (RU)"
                elif file_type == 'demo_en' and project.demo_link_en:
                    download_url = project.demo_link_en
                    file_name = "Демо (EN)"
        
        # Если нашли файл для скачивания
        if download_url:
            # Проверяем ОС только для установщиков (не для PDF инструкций)
            is_installer = file_type in ['installer_ru', 'installer_en', 'demo_ru', 'demo_en']
            
            if is_installer:
                # Определяем ОС пользователя
                user_os = detect_os(user_agent)
                
                # Если не Windows и пользователь еще не подтвердил скачивание
                if user_os != 'Windows' and request.GET.get('confirm') != 'yes':
                    # Показываем страницу предупреждения
                    return render(request, 'main_app/download_warning.html', {
                        'item_name': item_name,
                        'file_name': file_name,
                        'user_os': user_os,
                        'download_url': f"{request.path}?confirm=yes",
                        'file_type': file_type,
                        'slug': slug,
                    })
            
            # Отправляем уведомление в Telegram
            telegram_message = (
                f"📥 Скачивание файла!\n\n"
                f"📦 Продукт: {item_name or 'Неизвестно'}\n"
                f"📄 Файл: {file_name}\n"
                f"🔗 URL: {download_url}\n"
                f"💻 ОС: {detect_os(user_agent)}\n"
                f"🌐 IP: {ip_address}\n"
                f"🔍 Referer: {referer}\n"
                f"📱 User-Agent: {user_agent[:100]}"
            )
            
            try:
                send_telegram_message(telegram_message)
            except Exception as e:
                print(f"Ошибка отправки уведомления о скачивании в Telegram: {e}")
            
            # Редиректим на реальный файл
            return redirect(download_url)
        else:
            # Если файл не найден, возвращаем 404
            from django.http import Http404
            raise Http404("File not found")
            
    except Exception as e:
        print(f"Ошибка при отслеживании скачивания: {e}")
        # В случае ошибки все равно пытаемся редиректить, если URL есть
        if download_url:
            return redirect(download_url)
        from django.http import Http404
        raise Http404("File not found")

