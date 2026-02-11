# Generated manually for Contract model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Contract",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("contract_number", models.CharField(max_length=50, verbose_name="Номер договора")),
                ("doc_date", models.CharField(max_length=20, verbose_name="Дата договора")),
                ("act_date", models.CharField(max_length=20, verbose_name="Дата акта")),
                ("location", models.CharField(max_length=255, verbose_name="Место проведения работ")),
                ("total_cost", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Стоимость (руб.)")),
                ("work_list", models.JSONField(default=list, verbose_name="Перечень работ")),
                ("customer_data", models.JSONField(default=dict, verbose_name="Реквизиты заказчика")),
                ("contract_filename", models.CharField(blank=True, max_length=255, verbose_name="Файл договора")),
                ("act_filename", models.CharField(blank=True, max_length=255, verbose_name="Файл акта")),
                (
                    "payment_percent",
                    models.PositiveSmallIntegerField(blank=True, default=100, null=True, verbose_name="Процент предоплаты"),
                ),
                ("is_prepay", models.BooleanField(default=True, verbose_name="Предоплата")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="generated_contracts",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Кто создал",
                    ),
                ),
            ],
            options={
                "verbose_name": "Договор",
                "verbose_name_plural": "Договоры",
                "ordering": ["-created_at"],
            },
        ),
    ]
