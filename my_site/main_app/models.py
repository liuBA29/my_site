# main_app/models.py

from django.db import models
from cloudinary.models import CloudinaryField
from django.urls import reverse
from django.conf import settings





class PageView(models.Model):
    path = models.CharField(max_length=255, unique=True)
    views_count = models.PositiveIntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.path} — {self.views_count} просмотров"


class PageVisitLog(models.Model):
    path = models.CharField(max_length=255)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.viewed_at} - {self.path} - {self.ip_address}"



# 🔹 Модель для проектов
class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название проекта")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание проекта")
    tech_stack = models.CharField(max_length=255, verbose_name="Используемые технологии")  # Например: Django, React, PostgreSQL
    repo_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на репозиторий")
    demo_link_ru = models.URLField(blank=True, null=True, verbose_name="Ссылка на демо (ru)")
    demo_link_en = models.URLField(blank=True, null=True, verbose_name="Ссылка на демо (en)")
    image = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # 👈 Добавлено

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main_app:project_detail', kwargs={'slug':self.slug})

# 🔹 Абстрактная базовая модель для софта
class SoftwareBase(models.Model):
    """Базовая абстрактная модель с общими полями для FreeSoftware и BusinessSoftware"""
    name = models.CharField(max_length=200, verbose_name="Название софта")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание")
    download_link = models.URLField(verbose_name="Ссылка на скачивание", blank=True, null=True)
    english_link = models.URLField(verbose_name="English version link", blank=True, null=True)
    download_link_backup = models.URLField(verbose_name="Резервная ссылка (RU)", blank=True, null=True)
    english_link_backup = models.URLField(verbose_name="Резервная ссылка (EN)", blank=True, null=True)
    author = models.CharField(
        max_length=200,
        default="Liubov Kovaleva @LiuBA29",
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = CloudinaryField('image', blank=True, null=True)
    instruction_pdf = models.CharField(
        "Ссылка на PDF инструкцию",
        max_length=500,
        blank=True,
        null=True,
        help_text="Введите прямую ссылку на PDF файл (например, из Cloudinary) или имя файла из директории assets/pdf (например: USER_GUIDE.pdf)"
    )

    def get_pdf_url(self):
        """Получает URL для PDF файла - либо внешнюю ссылку, либо путь к статическому файлу"""
        if self.instruction_pdf:
            url = self.instruction_pdf.strip()
            if url:
                # Если это полный URL (начинается с http:// или https://), возвращаем его напрямую
                if url.startswith('http://') or url.startswith('https://'):
                    return url
                # Если это путь, начинающийся с /, возвращаем как есть
                elif url.startswith('/'):
                    return url
                # Иначе считаем это именем файла и формируем путь к статическим файлам
                else:
                    return f"{settings.STATIC_URL}assets/pdf/{url}"
        return None

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


# 🔹 Модель для бесплатного софта
class FreeSoftware(SoftwareBase):
    def get_absolute_url(self):
        return reverse('main_app:free_soft_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Бесплатный софт"
        verbose_name_plural = "Бесплатный софт"


# 🔹 Модель для софта для бизнеса
class BusinessSoftware(SoftwareBase):
    youtube_link = models.URLField(verbose_name="YouTube видео (ссылка)", blank=True, null=True)
    # Поля для тарифов
    demo_link = models.URLField(verbose_name="Ссылка на демо версию", blank=True, null=True, help_text="Ссылка на бесплатную демо версию")
    standard_price = models.CharField(max_length=100, verbose_name="Цена стандартной версии", blank=True, null=True, help_text="Например: '10000' или 'от 5000' (BYN будет добавлен автоматически)")
    show_pricing = models.BooleanField(default=False, verbose_name="Показывать блок тарифов", help_text="Включить отображение блока с тарифами (демо/стандарт/кастом)")

    def get_absolute_url(self):
        return reverse('main_app:business_soft_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Софт для бизнеса"
        verbose_name_plural = "Софт для бизнеса"




# 🔹 Модель для контактов (например, чтобы люди могли отправлять сообщения)
class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.name} ({self.email})"


# 🔹 Модель для заказов (заявок)
class Order(models.Model):
    # Статусы заказа
    STATUS_CHOICES = [
        ('new', 'Новая заявка'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнено'),
        ('cancelled', 'Отменён'),
    ]
    
    # Основная информация
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    # Данные клиента
    client_name = models.CharField(max_length=200, verbose_name="Имя клиента")
    client_email = models.EmailField(verbose_name="Email клиента")
    client_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Телефон"
    )
    
    # Описание заказа
    service_type = models.CharField(
        max_length=200, 
        verbose_name="Тип услуги",
        help_text="Например: Разработка сайта, Разработка софта, и т.д."
    )
    description = models.TextField(verbose_name="Описание задачи")
    
    # Информация о продукте (если заказ на конкретный продукт)
    product_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Название продукта",
        help_text="Название продукта, на который оформлен заказ"
    )
    product_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Версия продукта",
        help_text="Версия продукта (например: Standard, Custom, Demo)"
    )
    product_price = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Цена продукта",
        help_text="Цена продукта (например: 10000 BYN)"
    )
    
    # IP адрес для защиты от спама
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True, 
        verbose_name="IP адрес",
        help_text="IP адрес клиента (для защиты от спама)"
    )
    
    def __str__(self):
        return f"Заказ от {self.client_name} ({self.created_at.strftime('%d.%m.%Y')})"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']  # Сортировка: новые сначала