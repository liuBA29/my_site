# main_app/views.py

import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .forms import OrderForm
from .models import (
    BusinessSoftware,
    DownloadLog,
    ExternalLinkLog,
    FreeSoftware,
    Order,
    PageVisitLog,
    PageView,
    Project,
)
from .utils import get_client_ip
from accounts.views import send_telegram_message

logger = logging.getLogger(__name__)






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
    return render(request, 'main_app/index.html')



@login_required
def visits_log(request):
    """Страница с логами посещений, скачиваний и внешних ссылок - только для суперпользователя"""
    # Проверяем, что пользователь является суперпользователем
    if not request.user.is_superuser:
        raise Http404("Page not found")
    
    # Получаем последние 100 посещений
    visit_logs = PageVisitLog.objects.order_by('-viewed_at')[:100]
    
    # Получаем последние 100 скачиваний
    download_logs = DownloadLog.objects.order_by('-downloaded_at')[:100]
    
    # Получаем последние 100 переходов по внешним ссылкам
    external_link_logs = ExternalLinkLog.objects.order_by('-clicked_at')[:100]
    
    return render(request, 'main_app/visits_log.html', {
        'visit_logs': visit_logs,
        'download_logs': download_logs,
        'external_link_logs': external_link_logs
    })



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

def cooperation(request):
    return render(request, 'main_app/cooperation.html')

def ai_assistants(request):
    return render(request, 'main_app/ai_assistants.html')

def custom_crm(request):
    return render(request, 'main_app/custom_crm.html')

def desktop_apps(request):
    return render(request, 'main_app/desktop_apps.html')

def requisites(request):
    return render(request, 'main_app/requisites.html')

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
                    logger.exception("Ошибка отправки в Telegram")
                
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
            # Берём допустимые значения из choices формы, чтобы не дублировать
            form_for_choices = OrderForm()
            valid_values = [choice[0] for choice in form_for_choices.fields['service_type'].choices if choice[0]]
            if service_type in valid_values:
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
    soft = None

    try:
        # Определяем тип объекта и получаем его
        if slug:
            # Пробуем найти в FreeSoftware
            soft = FreeSoftware.objects.filter(slug=slug).first()
            if not soft:
                # Пробуем найти в BusinessSoftware
                soft = BusinessSoftware.objects.filter(slug=slug).first()
            
            if not soft:
                logger.debug("Объект с slug=%s не найден ни в FreeSoftware, ни в BusinessSoftware", slug)

            if soft:
                logger.debug("Найден soft: %s, тип: %s", soft.name, type(soft).__name__)
                item_name = soft.name
                if file_type == 'pdf_instruction' and soft.instruction_pdf:
                    download_url = soft.get_pdf_url()
                    file_name = "PDF инструкция"
                elif file_type == 'pdf_instruction_en':
                    if isinstance(soft, BusinessSoftware) and soft.instruction_pdf_en:
                        download_url = soft.get_pdf_url_en()
                        file_name = "PDF Instruction (EN)"
                elif file_type == 'installer_ru' and soft.download_link:
                    download_url = soft.download_link
                    file_name = "Установщик (RU)"
                elif file_type == 'installer_en' and soft.english_link:
                    download_url = soft.english_link
                    file_name = "Установщик (EN)"
                # Обработка демо-версий для BusinessSoftware
                elif file_type in ['demo_ru', 'demo_en']:
                    # Проверяем наличие атрибута demo_link (он есть только у BusinessSoftware)
                    if hasattr(soft, 'demo_link'):
                        demo_link_value = soft.demo_link
                        if demo_link_value:
                            download_url = demo_link_value
                            file_name = "Демо версия" if file_type == 'demo_ru' else "Демо версия (EN)"
                        else:
                            logger.debug("Объект %s: demo_link пустой или None", slug)
                    else:
                        logger.debug("Объект %s не имеет атрибута demo_link (тип: %s)", slug, type(soft).__name__)
        
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
        
        if not download_url:
            logger.debug("Не удалось найти download_url для file_type=%s, slug=%s", file_type, slug)
            if soft:
                logger.debug("soft.demo_link = %s", getattr(soft, 'demo_link', 'НЕТ АТРИБУТА'))
        
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
            
            # Сохраняем информацию о скачивании в лог
            try:
                DownloadLog.objects.create(
                    product_name=item_name or 'Неизвестно',
                    file_name=file_name or 'Неизвестно',
                    file_type=file_type,
                    download_url=download_url,
                    ip_address=ip_address,
                    user_agent=user_agent[:500] if user_agent else None,
                    referer=referer[:500] if referer else None,
                    user_os=detect_os(user_agent)
                )
            except Exception as e:
                logger.exception("Ошибка сохранения лога скачивания")

            return redirect(download_url)
        else:
            raise Http404("File not found")

    except Exception as e:
        logger.exception("Ошибка при отслеживании скачивания")
        if download_url:
            return redirect(download_url)
        raise Http404("File not found")


def track_link(request, link_type, slug=None):
    """
    Отслеживает переходы по внешним ссылкам (YouTube, репозитории и т.д.)
    
    link_type: 'youtube', 'repo', 'other'
    slug: slug объекта (для soft или project)
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    referer = request.META.get('HTTP_REFERER', 'Unknown')
    
    link_url = None
    item_name = None
    
    try:
        if slug:
            # Пробуем найти в FreeSoftware
            soft = FreeSoftware.objects.filter(slug=slug).first()
            if not soft:
                # Пробуем найти в BusinessSoftware
                soft = BusinessSoftware.objects.filter(slug=slug).first()
            
            if soft:
                item_name = soft.name
                if link_type == 'youtube' and hasattr(soft, 'youtube_link') and soft.youtube_link:
                    link_url = soft.youtube_link
        
        # Если не нашли в soft, пробуем Project
        if not link_url and slug:
            project = Project.objects.filter(slug=slug).first()
            if project:
                item_name = project.title
                if link_type == 'repo' and project.repo_link:
                    link_url = project.repo_link
        
        # Если нашли ссылку
        if link_url:
            # Сохраняем информацию о переходе в лог
            try:
                ExternalLinkLog.objects.create(
                    link_type=link_type,
                    product_name=item_name or 'Неизвестно',
                    link_url=link_url,
                    ip_address=ip_address,
                    user_agent=user_agent[:500] if user_agent else None,
                    referer=referer[:500] if referer else None,
                    user_os=detect_os(user_agent)
                )
            except Exception as e:
                logger.exception("Ошибка сохранения лога внешней ссылки")

            return redirect(link_url)
        else:
            raise Http404("Link not found")

    except Exception as e:
        logger.exception("Ошибка при отслеживании внешней ссылки")
        if link_url:
            return redirect(link_url)
        raise Http404("Link not found")

