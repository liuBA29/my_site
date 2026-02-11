# Связь договора с клиентом

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contract_maker", "0005_add_test_customers"),
    ]

    operations = [
        migrations.AddField(
            model_name="contract",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="contracts",
                to="contract_maker.customer",
                verbose_name="Клиент (заказчик)",
            ),
        ),
    ]
