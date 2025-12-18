# main_app/models.py

from django.db import models
from cloudinary.models import CloudinaryField
from django.urls import reverse





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

# 🔹 Модель для бесплатного софта
class FreeSoftware(models.Model):
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main_app:free_soft_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Бесплатный софт"
        verbose_name_plural = "Бесплатный софт"


# 🔹 Модель для софта для бизнеса
class BusinessSoftware(models.Model):
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
    youtube_link = models.URLField(verbose_name="YouTube видео (ссылка)", blank=True, null=True)

    def __str__(self):
        return self.name

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
    
    def __str__(self):
        return f"Заказ от {self.client_name} ({self.created_at.strftime('%d.%m.%Y')})"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']  # Сортировка: новые сначала
