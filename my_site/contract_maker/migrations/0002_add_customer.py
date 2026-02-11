# Generated for Customer model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contract_maker", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("org_name", models.CharField(max_length=255, verbose_name="Наименование организации")),
                (
                    "rep_position",
                    models.CharField(blank=True, default="", max_length=100, verbose_name="Должность представителя"),
                ),
                (
                    "rep_name",
                    models.CharField(blank=True, default="", max_length=255, verbose_name="ФИО представителя"),
                ),
                (
                    "basis",
                    models.CharField(blank=True, default="Устава", max_length=255, verbose_name="Действует на основании"),
                ),
                (
                    "short_name",
                    models.CharField(blank=True, default="", max_length=100, verbose_name="Краткая подпись (в реквизитах)"),
                ),
                ("address", models.CharField(blank=True, default="", max_length=500, verbose_name="Адрес")),
                ("unp", models.CharField(blank=True, default="", max_length=20, verbose_name="УНП")),
                ("okpo", models.CharField(blank=True, default="", max_length=20, verbose_name="ОКПО")),
                ("iban", models.CharField(blank=True, default="", max_length=50, verbose_name="IBAN")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contract_customers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Кто добавил",
                    ),
                ),
            ],
            options={
                "verbose_name": "Клиент",
                "verbose_name_plural": "Клиенты",
                "ordering": ["org_name"],
            },
        ),
    ]
