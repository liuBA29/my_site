# Generated manually for WorkType (Виды работ)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contract_maker", "0006_add_contract_customer_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Наименование вида работ")),
                ("order", models.PositiveIntegerField(blank=True, default=0, verbose_name="Порядок")),
            ],
            options={
                "verbose_name": "Вид работ",
                "verbose_name_plural": "Виды работ",
                "ordering": ["order", "name"],
            },
        ),
    ]
